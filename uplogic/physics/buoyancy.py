from bge import logic
from mathutils import Vector
from uplogic.utils.math import vec_clamp
from uplogic.utils.raycasting import raycast
from uplogic.utils.constants import FLOTSAM
from uplogic.utils.constants import SHIP
from uplogic.utils.constants import WATER
from uplogic import console


class ULBuoy():
    '''Base class for all buoyancy objects.

    Tracks the active state shared by all buoyancy subclasses.
    Not intended for direct use.
    '''

    def __init__(self) -> None:
        '''Initialise the buoy with ``_active`` set to ``True``.
        '''
        self._active = True

    def disable(self):
        '''Pause the buoyancy simulation for this object.

        The ``update`` callback remains registered in ``pre_draw`` but returns
        immediately until :meth:`enable` is called.
        '''
        self._active = False

    def enable(self):
        '''Resume the buoyancy simulation for this object after a call to
        :meth:`disable`.
        '''
        self._active = True

    def destroy(self):
        '''Remove this buoy from the scene update loop.

        :raises NotImplementedError: Must be implemented by subclasses.
        '''
        raise NotImplementedError


class Flotsam(ULBuoy):
    '''Single-object buoyancy simulation.

    Each frame a ray is cast upward from ``game_object`` looking for a surface
    tagged ``WATER``.  When the ray hits, an upward impulse proportional to the
    depth below the water surface is applied, simulating buoyancy.  If
    ``align`` is ``True`` the object is also gently tilted to match the water
    surface normal.

    Linear and angular damping are raised while the object is submerged and
    lowered to a low value when it is in open air.

    :param game_object: The game object to apply buoyancy to.  The instance is
        stored on the object under the ``FLOTSAM`` property key.
    :param buoyancy: Buoyancy multiplier.  Higher values produce a stronger
        upward force.
    :param height: Maximum ray length used to search for a water surface above
        the object.
    :param align: When ``True``, align the object's Z axis to the water surface
        normal each frame.
    '''

    _deprecated = False

    def __init__(self, game_object, buoyancy=1, height=200, align=True) -> None:
        '''Initialise buoyancy for ``game_object`` and register the per-frame
        update callback.

        :param game_object: The game object that will float.
        :param buoyancy: Buoyancy force multiplier.
        :param height: Ray search distance above the object for the water
            surface.
        :param align: Align the object's Z axis to the water normal each frame.
        '''
        if self._deprecated:
            console.warning('ULFlotsam class will be renamed to "Flotsam" in future releases!')
        super().__init__()
        self.game_object = game_object
        game_object[FLOTSAM] = self
        self.height = height
        self.buoyancy = buoyancy
        self.align = align
        logic.getCurrentScene().pre_draw.append(self.update)

    def update(self):
        '''Per-frame update called via ``pre_draw``.

        Casts a ray upward to locate a ``WATER``-tagged surface.  If a surface
        is found an upward impulse is applied scaled by the distance from the
        object to the surface and the ``buoyancy`` factor.  Linear and angular
        damping are set to high values while submerged and reset to low values
        in air.
        '''
        if not self._active:
            return
        up = Vector((0, 0, 1))
        flotsam = self.game_object
        lindamp = .1
        wpos = flotsam.worldPosition
        ray = raycast(
            flotsam,
            wpos,
            up,
            self.height,
            WATER,
            xray=True,
            local=True,
            visualize=True
        )
        if ray.obj:
            lindamp = .8
            lift = (up * (wpos - ray.point).length * self.buoyancy)
            flotsam.applyImpulse(
                wpos,
                vec_clamp(lift, max=self.buoyancy),
                False
            )
            if self.align:
                self.game_object.alignAxisToVect(ray.normal, 2, .2)
        flotsam.linearDamping = lindamp
        flotsam.angularDamping = lindamp * .8

    def destroy(self):
        '''Remove the per-frame update callback and stop the buoyancy
        simulation.
        '''
        logic.getCurrentScene().pre_draw.remove(self.update)


class ULFlotsam(Flotsam):
    '''[DEPRECATED] Use :class:`Flotsam` instead.'''
    _deprecated = True


class Ship(ULBuoy):
    '''Multi-point buoyancy simulation for a ship or large vessel.

    Child objects whose names contain ``"Buoy"`` (sorted alphabetically) act as
    individual buoyancy sample points.  Each frame every buoy casts an upward
    ray to locate a ``WATER``-tagged surface.  When a buoy is submerged, its
    share of the total buoyant lift (``1 / number_of_buoys``) is applied as an
    impulse to the parent ship at that buoy's world position.  Linear and
    angular damping are also adjusted dynamically: the more buoys are
    submerged, the higher the damping, up to a capped maximum.

    :param game_object: The ship game object.  Child objects named ``Buoy*``
        are collected as buoyancy sample points.  The instance is stored on the
        object under the ``SHIP`` property key.
    :param buoyancy: Buoyancy force multiplier applied at each buoy point.
    :param height: Maximum ray length used to search for a water surface above
        each buoy.
    :param water: Optional game object to tag as ``WATER`` so the ship's buoys
        can detect it.
    '''

    _deprecated = False

    def __init__(self, game_object, buoyancy=1, height=200, water=None) -> None:
        '''Initialise buoyancy for ``game_object``, collect buoy child objects,
        and register the per-frame update callback.

        :param game_object: The ship game object whose ``Buoy*`` children will
            be used as buoyancy sample points.
        :param buoyancy: Per-buoy force multiplier.
        :param height: Ray search distance above each buoy for the water
            surface.
        :param water: If provided, the ``WATER`` property is set on this object
            so it is recognised by the raycaster.
        '''
        if self._deprecated:
            console.warning('ULShip class will be renamed to "Ship" in future releases!')
        super().__init__()
        self.game_object = game_object
        self.linear_damping = game_object.linearDamping
        self.angular_damping = game_object.angularDamping
        game_object[SHIP] = self
        self.height = height
        if water:
            water[WATER] = True
        cs = sorted(game_object.childrenRecursive, key=lambda c: c.name)
        self.buoys = [c for c in cs if 'Buoy' in c.name]
        self.buoyancy = buoyancy
        logic.getCurrentScene().pre_draw.append(self.update)

    def update(self):
        '''Per-frame update called via ``pre_draw``.

        Iterates over all buoy child objects.  For each buoy that is below a
        ``WATER`` surface, a proportional upward impulse (scaled by
        ``1 / total_buoys``) is applied to the ship at that buoy's world
        position.  Linear and angular damping accumulate proportionally to the
        number of submerged buoys, up to a maximum headroom above the ship's
        baseline damping values.
        '''
        if not self._active:
            return
        up = Vector((0, 0, 1))
        lifts = len(self.buoys)
        ship = self.game_object
        max_lin_damp = .9 - self.linear_damping
        max_ang_damp = .8 - self.linear_damping
        lin_dampen_factor = 0
        ang_dampen_factor = 0
        for buoy in self.buoys:
            wpos = buoy.worldPosition
            ray = raycast(
                buoy,
                wpos,
                up,
                self.height,
                WATER,
                xray=True,
                local=True
            )
            if ray.obj:
                div = 1 / lifts
                lin_dampen_factor += (max_lin_damp * div)
                ang_dampen_factor += (max_ang_damp * div)
                lift = (up * (wpos - ray.point).length * self.buoyancy) * div
                ship.applyImpulse(
                    wpos,
                    vec_clamp(lift, max=self.buoyancy * 2 * div),
                    False
                )
        ship.linearDamping = self.linear_damping + lin_dampen_factor
        ship.angularDamping = self.angular_damping + ang_dampen_factor

    def destroy(self):
        '''Remove the per-frame update callback and stop the buoyancy
        simulation.
        '''
        logic.getCurrentScene().pre_draw.remove(self.update)


class ULShip(Ship):
    '''[DEPRECATED] Use :class:`Ship` instead.'''
    _deprecated = True

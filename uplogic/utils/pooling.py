'''Object pooling system for uplogic. Provides ``SpawnPool``, ``Spawn``,
and built-in projectile subclasses.
'''
from bge import logic
from uplogic.events import schedule
from bge.types import KX_GameObject as GameObject
import bpy
from mathutils import Vector, Matrix
from .math import get_bitmask
from .raycasting import raycast, raycast_projectile
from .math import cycle
from .visuals import draw_cube
from .constants import RED, WHITE
from uplogic import console


class Spawn:
    '''A single object instance managed by a :class:`SpawnPool`.

    On construction the class claims one of the pool's pre-created
    ``KX_GameObject`` instances (setting its ``'spawn'`` property to
    ``self``), copies the spawner transform, and registers ``_update`` as a
    ``pre_draw`` callback.  After ``_lifetime`` seconds the event system
    automatically calls :meth:`destroy`.

    Override :meth:`start`, :meth:`update`, and :meth:`stop` to add custom
    behaviour without touching the pool lifecycle.
    '''

    def __init__(self, object: GameObject, pool) -> None:
        '''Initialise and activate a spawn.

        :param object: the ``KX_GameObject`` claimed from the pool; may be
            ``None`` when the pool has no spare objects.
        :param pool: the owning :class:`SpawnPool` instance.
        '''
        schedule(self.destroy, pool._lifetime)
        schedule(self._reset_physics)
        self._pool = pool
        self._object = None
        self.scene = logic.getCurrentScene()
        if object and object['spawn'] is None:
            self._object = object
            object.restorePhysics()
            object['spawn'] = self
        if pool.spawner:
            self.transform = pool.spawner.worldTransform.copy()
            self.position = pool.spawner.worldPosition.copy()
            self.orientation = pool.spawner.worldOrientation.copy()
        else:
            self.transform = Matrix()
            self.position = Vector((0, 0, 0))
            self.orientation = Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        scene = logic.getCurrentScene()
        if self._update not in scene.pre_draw:
            scene.pre_draw.append(self._update)
        self._visualize = False
        self.start()

    def _reset_physics(self):
        '''Reset scale and velocities on the underlying object.

        Internal; called via the event scheduler immediately after
        construction so that any residual motion from a previous spawn cycle
        is cleared before :meth:`start` logic runs.
        '''
        object = self._object
        if not object:
            return
        object.worldScale = (1, 1, 1)
        object.worldLinearVelocity = (0, 0, 0)
        object.worldAngularVelocity = (0, 0, 0)

    @property
    def transform(self):
        '''Full world transform ``Matrix`` of the spawn.

        Setting this property also updates ``worldTransform`` on the
        underlying ``KX_GameObject`` when one is assigned.
        '''
        return self._transform

    @transform.setter
    def transform(self, pos):
        self._transform = pos
        if self._object:
            self._object.worldTransform = self._transform

    @property
    def position(self):
        '''World-space position ``Vector`` of the spawn.

        Setting this property also updates ``worldPosition`` on the
        underlying ``KX_GameObject`` when one is assigned.
        '''
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        if self._object:
            self._object.worldPosition = self._position

    @property
    def orientation(self):
        '''World-space orientation ``Matrix`` of the spawn.

        Setting this property also updates ``worldOrientation`` on the
        underlying ``KX_GameObject`` when one is assigned.
        '''
        return self._orientation

    @orientation.setter
    def orientation(self, ori):
        self._orientation = ori
        if self._object:
            self._object.worldOrientation = self._orientation

    @property
    def game_object(self):
        '''Read-only alias for the underlying ``KX_GameObject`` (``_object``).'''
        return self._object

    @game_object.setter
    def game_object(self, val):
        console.debug("Attribute 'game_object' of 'Spawn' is read-only!")

    def start(self):
        '''Override hook called at the end of :meth:`__init__`.

        Implement custom initialisation logic in subclasses; the default
        implementation does nothing.
        '''
        pass

    def _update(self):
        '''Internal ``pre_draw`` callback; runs optional visualisation then calls :meth:`update`.'''
        if self._visualize:
            draw_cube(self.position, 1, centered=True)
        self.update()

    def update(self):
        '''Override hook called every tick via the ``pre_draw`` callback.

        Implement per-frame logic in subclasses; the default implementation
        does nothing.
        '''
        pass

    def destroy(self):
        '''Return the object to the pool and call :meth:`stop`.

        Removes the ``pre_draw`` callback, moves the object to the pool's
        ``_reset_pos``, zeroes its scale, clears the ``'spawn'`` property,
        and suspends physics.  Called automatically by the event scheduler
        after ``_lifetime`` seconds, but may also be called manually.
        '''
        scene = logic.getCurrentScene()
        if self._update in scene.pre_draw:
            scene.pre_draw.remove(self._update)
        obj = self._object
        if obj and obj['spawn'] is self:
            obj.worldPosition = self._pool._reset_pos
            obj.worldScale = (.001, .001, .001)
            obj['spawn'] = None
            obj.suspendPhysics()
        self.stop()

    def stop(self):
        '''Override hook called at the end of :meth:`destroy`.

        Implement cleanup logic in subclasses; the default implementation
        does nothing.
        '''
        pass


class SpawnedInstance(Spawn):
    '''A :class:`Spawn` variant whose pool objects are full data copies.

    Unlike :class:`Spawn`, each pool object is duplicated with its full
    Blender data and logic-tree state.  :meth:`_reset_physics` additionally
    resets the ``logictree._initialized`` flag on every component so that
    logic trees restart cleanly on reuse.
    '''

    def __init__(self, object: GameObject, pool) -> None:
        '''Initialise a spawned instance.

        :param object: the ``KX_GameObject`` claimed from the pool; may be
            ``None`` when the pool has no spare objects.
        :param pool: the owning :class:`SpawnPool` instance.
        '''
        super().__init__(object=object, pool=pool)
        # schedule(self.destroy, pool._lifetime)
        #     self._pool = pool
        #     self._object = None
        #     self.scene = logic.getCurrentScene()
        #     if object and object['spawn'] is None:
        #         self._object = object
        #         object.worldPosition = (0, 0, 0)
        #         object.worldScale = (1, 1, 1)
        #         object['spawn'] = self
        #         object.restorePhysics()
        #         object.worldLinearVelocity = (0, 0, 0)
        #         object.worldAngularVelocity = (0, 0, 0)
        #     if pool.spawner:
        #         self.transform = pool.spawner.worldTransform.copy()
        #         self.position = pool.spawner.worldPosition.copy()
        #         self.orientation = pool.spawner.worldOrientation.copy()
        #     else:
        #         self.transform = Matrix()
        #         self.position = Vector((0, 0, 0))
        #         self.orientation = Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        #     scene = logic.getCurrentScene()
        #     if self._update not in scene.pre_draw:
        #         scene.pre_draw.append(self._update)
        #     self._visualize = False
        #     self.start()

    def _reset_physics(self):
        '''Reset scale, velocities, and logic-tree state on the underlying object.

        Calls the parent :meth:`Spawn._reset_physics`, then iterates over all
        components and resets ``logictree._initialized`` to ``False`` so that
        logic trees restart from their initial state on the next spawn cycle.
        '''
        super()._reset_physics()
        for c in self._object.components:
            tree = getattr(c, 'logictree', None)
            if tree:
                tree.network._initialized = False

    @property
    def transform(self):
        '''Full world transform ``Matrix`` of the spawn.

        When an object is assigned, reads directly from ``worldTransform``
        rather than the cached ``_transform``.
        '''
        return self._object.worldTransform if self._object else self._transform

    @transform.setter
    def transform(self, pos):
        self._transform = pos
        if self._object:
            self._object.worldTransform = self._transform

    @property
    def position(self):
        '''World-space position ``Vector`` of the spawn.

        When an object is assigned, reads directly from ``worldPosition``
        rather than the cached ``_position``.
        '''
        return self._object.worldPosition if self._object else self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        if self._object:
            self._object.worldPosition = self._position

    @property
    def orientation(self):
        '''World-space orientation ``Matrix`` of the spawn.

        When an object is assigned, reads directly from ``worldOrientation``
        rather than the cached ``_orientation``.
        '''
        return self._object.worldOrientation if self._object else self._orientation

    @orientation.setter
    def orientation(self, ori):
        self._orientation = ori
        if self._object:
            self._object.worldOrientation = self._orientation

    @property
    def game_object(self):
        '''Read-only alias for the underlying ``KX_GameObject`` (``_object``).'''
        return self._object

    @game_object.setter
    def game_object(self, val):
        console.debug("Attribute 'game_object' of 'Spawn' is read-only!")

    def start(self):
        '''Override hook called at the end of :meth:`__init__`; does nothing by default.'''
        pass

    def _update(self):
        '''Internal ``pre_draw`` callback; runs optional visualisation then calls :meth:`update`.'''
        if self._visualize:
            draw_cube(self.position, 1, color=WHITE if self._object else RED, centered=True)
        self.update()

    def update(self):
        '''Override hook called every tick via the ``pre_draw`` callback; does nothing by default.'''
        pass

    def destroy(self):
        '''Return the object to the pool and call :meth:`stop`.

        Mirrors :meth:`Spawn.destroy`: removes the ``pre_draw`` callback,
        parks the object at ``_reset_pos``, zeroes its scale, clears the
        ``'spawn'`` property, and suspends physics.
        '''
        scene = logic.getCurrentScene()
        if self._update in scene.pre_draw:
            scene.pre_draw.remove(self._update)
        obj = self._object
        if obj and obj['spawn'] is self:
            obj.worldPosition = self._pool._reset_pos
            obj.worldScale = (.001, .001, .001)
            obj['spawn'] = None
            obj.suspendPhysics()
        self.stop()

    def stop(self):
        '''Override hook called at the end of :meth:`destroy`; does nothing by default.'''
        pass


class SimpleBullet(Spawn):
    '''Raycast-based bullet that travels in a straight line at ``speed`` units per tick.

    Each tick :meth:`update` casts a ray from the current position to the next
    position.  If nothing is hit the bullet advances; if a hit occurs
    :meth:`hit` is called and the bullet is destroyed.  Override :meth:`hit`
    to react to the impact.
    '''

    speed = 20

    def update(self):
        '''Advance the bullet one tick, or destroy it on impact.

        Casts a ray from the current ``position`` to the next position along
        the bullet's local Y axis.  Calls :meth:`hit` with the
        :class:`~uplogic.utils.raycasting.RayCastData` on impact, then calls
        :meth:`destroy`.
        '''
        target = self.position + Vector((0, self.speed, 0)) @ self.transform.inverted()
        dat = raycast(
            self.game_object if self.game_object else self.scene.active_camera,
            self.position,
            target,
            mask=self._pool.raycast_mask
        )

        if not dat.obj:
            self.position = target
        else:
            self.hit(dat)
            self.destroy()

    def hit(self, data):
        '''Override hook called when the bullet strikes an object.

        :param data: :class:`~uplogic.utils.raycasting.RayCastData` describing
            the impact; the default implementation does nothing.
        '''
        pass


class PhysicsBullet(Spawn):
    '''Parabolic bullet using :func:`~uplogic.utils.raycasting.raycast_projectile`.

    :meth:`start` records the initial aim vector.  Each tick :meth:`update`
    follows the current arc segment; when a hit occurs :meth:`hit` is called
    and the bullet is destroyed.  The object's Y-axis is aligned to the
    current direction of travel each tick.
    '''

    speed = 30

    def start(self):
        '''Record the initial aim vector from the spawner transform.'''
        self.target = Vector((0, 1, 0)) @ self.transform.inverted()

    def update(self):
        '''Advance the bullet one tick along the parabolic arc, or destroy it on impact.

        Calls :func:`~uplogic.utils.raycasting.raycast_projectile` from the
        current position towards ``self.target``.  Aligns the object's Y-axis
        to the current direction, advances ``position`` to the arc endpoint,
        and updates ``target`` to the direction of the last segment.  On a
        hit, calls :meth:`hit` then :meth:`destroy`.
        '''
        dat = raycast_projectile(
            self.game_object if self.game_object else self.scene.active_camera,
            self.position,
            self.target,
            power=self.speed * 10,
            distance=self.speed,
            visualize=self._visualize,
            local=True,
            mask=self._pool.raycast_mask
        )
        if self.game_object:
            self.game_object.alignAxisToVect(self.target, 1, 1.0)

        if not dat.obj:
            self.position = dat.points[-1]
            self.target = dat.points[-1] - dat.points[-2]
        else:
            self.hit(dat)
            self.destroy()

    def hit(self, data):
        '''Override hook called when the bullet strikes an object.

        :param data: :class:`~uplogic.utils.raycasting.RayCastDataProjectile`
            describing the impact; the default implementation does nothing.
        '''
        pass


class SpawnPool:
    '''Manages a fixed-size pool of pre-created BGE objects.

    On construction the pool duplicates *object_name* exactly *amount* times,
    parks each copy at *inactive_pos*, suspends its physics, and tags it with
    ``game_object['spawn'] = None``.  Calling :meth:`spawn` claims the next
    available object using a round-robin index and returns a new *spawn*
    instance wrapping it.
    '''

    _spawn_idx = 0

    def __init__(
        self,
        object_name: str,
        amount: int = 10,
        lifetime: float = 5,
        spawner=None,
        spawn=Spawn,
        raycast_mask=get_bitmask(all=True),
        inactive_pos: Vector = Vector((0, 0, -100)),
        visualize: bool = False
    ):
        '''Initialise the pool and pre-create all objects.

        :param object_name: Blender object name to duplicate for the pool.
        :param amount: number of objects to pre-create.
        :param lifetime: time in seconds before each :class:`Spawn` is
            automatically destroyed.
        :param spawner: reference ``KX_GameObject`` whose transform is copied
            to each new spawn; when ``None`` the identity transform is used.
        :param spawn: :class:`Spawn` subclass to instantiate on each
            :meth:`spawn` call.
        :param raycast_mask: collision mask forwarded to bullet subclasses.
        :param inactive_pos: world-space ``Vector`` where inactive pool objects
            are parked.
        :param visualize: when ``True``, each :class:`Spawn` draws a debug
            cube at its position every tick.
        '''
        self.spawn_cls = spawn
        # self._spawn_idx = 0
        self.spawner = spawner
        self.raycast_mask = raycast_mask
        self._amount = amount # clamp(amount, 0, 10)
        self._lifetime = lifetime

        self.visualize = visualize
        if object_name:
            bobj = bpy.data.objects[object_name]
            self._spawn_name = f'Spawned{bobj.name}'
            self.scene = logic.getCurrentScene()
            self._reset_pos = inactive_pos
            for x in range(self._amount):
                if self.scene.objects.get(f'{self._spawn_name}{x}'):
                    continue
                if spawn is SpawnedInstance:
                    bspawn = bobj.copy()
                    bspawn.name = f'{self._spawn_name}{x}'
                else:
                    bspawn = bpy.data.objects.new(f'{self._spawn_name}{x}', bobj.data)
                    bspawn.game.physics_type = bobj.game.physics_type
                bpy.context.collection.objects.link(bspawn)
                bspawn.location = Vector(inactive_pos)
                bspawn.scale = Vector((.001, .001, .001))
                gobj = self.scene.convertBlenderObject(bspawn)
                gobj['spawn'] = None
                gobj.suspendPhysics()
        else:
            self._spawn_name = None

    def spawn(self):
        '''Claim the next available pool object and return a new spawn instance.

        Uses a round-robin index over the pool to select the next object, then
        constructs a :attr:`spawn_cls` instance wrapping it.

        :returns: a new instance of the configured :class:`Spawn` subclass.
        '''
        spawn_obj = self.scene.objects[f'{self._spawn_name}{self._spawn_idx}'] if self._spawn_name else None
        spawn = self.spawn_cls(spawn_obj, self)
        spawn._visualize = self.visualize
        self.__class__._spawn_idx = cycle(self._spawn_idx + 1, 0, self._amount - 1)
        return spawn

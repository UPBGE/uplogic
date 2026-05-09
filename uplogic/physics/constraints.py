from bge import constraints
from bge import logic
from bge import render
from bge.types import KX_ConstraintWrapper as GameConstraint
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.utils.math import get_direction
from uplogic.utils.objects import set_curve_points
from uplogic.utils.objects import xrot_to
from uplogic.utils.objects import yrot_to
from uplogic.utils.objects import zrot_to
from uplogic import console


CONSTRAINT_TYPES = {
    'point': 0,
    'hinge': 1,
    'angular': 2,
    'conetwist': 3,
    'generic6dof': 4
}
'''Mapping of human-readable constraint type names to the integer IDs expected
by ``bge.constraints.createConstraint()``.
'''


def create_constraint(
    obj: GameObject,
    target: GameObject,
    constraint_type: int or str = 0,
    pivot: set = (0, 0, 0),
    limit: set = (0, 0, 0),
    linked_collision: bool = True,
    local: bool = True
) -> GameConstraint:
    '''Wrapper for ``bge.constraints.createConstraint()``.

    Creates a physics constraint between ``obj`` and ``target``.  The
    ``constraint_type`` may be given as an integer or as one of the string
    keys defined in :data:`CONSTRAINT_TYPES` (``'point'``, ``'hinge'``,
    ``'angular'``, ``'conetwist'``, ``'generic6dof'``).

    :param obj: The game object the constraint is applied to.
    :param target: The game object the constraint connects to.
    :param constraint_type: Type of constraint as an integer ID or a string
        key from :data:`CONSTRAINT_TYPES`.  Defaults to ``0`` (point
        constraint).
    :param pivot: World-space (or local-space when ``local=True``) point of
        application for the constraint.
    :param limit: Axis-limit values passed to ``createConstraint()`` (e.g.
        acting as a doorstop on the constrained axes).
    :param linked_collision: When ``True``, collision between ``obj`` and
        ``target`` remains enabled.  Set to ``False`` to disable it.
    :param local: When ``True`` the ``pivot`` coordinates are interpreted in
        ``obj``'s local space.  When ``False`` they are converted from world
        space by subtracting ``obj.worldPosition``.
    :returns: The created ``KX_ConstraintWrapper`` instance.
    '''
    if not local:
        pivot[0] -= obj.worldPosition.x
        pivot[1] -= obj.worldPosition.y
        pivot[2] -= obj.worldPosition.z
    return constraints.createConstraint(
        obj.getPhysicsId(),
        target.getPhysicsId(),
        constraint_type if isinstance(constraint_type, int) else CONSTRAINT_TYPES.get(constraint_type, 0),
        pivot[0],
        pivot[1],
        pivot[2],
        limit[0],
        limit[1],
        limit[2],
        0 if linked_collision else 128
    )


def remove_constraint(constraint: GameConstraint) -> None:
    '''Wrapper for ``bge.constraints.removeConstraint()``.

    Removes an existing physics constraint from the simulation.

    :param constraint: The ``KX_ConstraintWrapper`` to remove.
    '''
    constraints.removeConstraint(constraint.getConstraintId())


class TrackTo():
    '''Continuously rotates a game object to face a target point or object.

    On each frame the chosen rotation function (``xrot_to``, ``yrot_to``, or
    ``zrot_to``) is called via the ``pre_draw`` callback to orient
    ``game_object`` toward ``target``.  Setting the ``axis`` property
    re-registers the update callback, so the axis can be changed at runtime.

    :param game_object: The object to rotate.
    :param target: The point or object to track.  A list or tuple is converted
        to a ``Vector``; a ``Vector`` is used directly.
    :param axis: Local axis to align toward the target.  ``0`` = X, ``1`` = Y,
        ``2`` = Z (default).
    :param front: Local axis index that should face the target (passed directly
        to the underlying rotation helper).
    :param factor: Tracking speed factor passed to the rotation helper as the
        interpolation strength.
    '''

    _deprecated = False

    def __init__(
        self,
        game_object: GameObject,
        target: GameObject or Vector,
        axis: int = 2,
        front: int = 1,
        factor: float = 1
    ) -> None:
        '''Initialise the TrackTo constraint and register the update callback.

        Setting ``self.axis`` in the constructor is intentionally side-effecting:
        it selects the rotation function and appends ``self.update`` to the
        scene's ``pre_draw`` list.

        :param game_object: The object to rotate each frame.
        :param target: Point or object to track.  Lists and tuples are
            converted to ``Vector``.
        :param axis: Local axis index (0/1/2) to align toward the target.
        :param front: Local axis that should point toward the target, passed
            to the underlying rotation helper.
        :param factor: Interpolation strength / tracking speed forwarded to
            the rotation helper.
        '''
        if self._deprecated:
            console.warning('ULTrackTo class will be renamed to "TrackTo" in future releases!')
        self._axis = None
        self._target = None
        self.game_object = game_object
        self.target = target
        self.front = front
        self.factor = factor
        self.axis = axis

    @property
    def target(self):
        '''The world-space point or object currently being tracked.

        :returns: A ``Vector`` representing the tracked position.
        '''
        return self._target

    @target.setter
    def target(self, val):
        '''Set the tracking target.

        Converts a ``list`` or ``tuple`` to a ``Vector``.  Accepts a
        ``Vector`` directly.  Logs an error and leaves the target unchanged
        for any other type.

        :param val: New target value — ``list``, ``tuple``, or ``Vector``.
        '''
        if isinstance(val, list) or isinstance(val, tuple):
            self._target = Vector(val)
        elif isinstance(val, Vector):
            self._target = val
        else:
            console.error('Could not set TrackTo target!')

    @property
    def axis(self):
        '''The local axis index currently used to face the target.

        :returns: Integer axis index (``0`` = X, ``1`` = Y, ``2`` = Z).
        '''
        return self._axis

    @axis.setter
    def axis(self, val):
        '''Set the tracking axis and (re-)register the ``update`` callback.

        Selects ``xrot_to``, ``yrot_to``, or ``zrot_to`` based on ``val``
        (``0``, ``1``, or ``2`` respectively).  Any other value disables
        rotation.  Appends ``self.update`` to the current scene's ``pre_draw``
        list as a side effect.

        :param val: Axis index — ``0`` for X, ``1`` for Y, ``2`` for Z.
        '''
        if val == 0:
            self.rotate_func = xrot_to
        elif val == 1:
            self.rotate_func = yrot_to
        elif val == 2:
            self.rotate_func = zrot_to
        else:
            self.rotate_func = None
        self._axis = val
        logic.getCurrentScene().pre_draw.append(self.update)

    def remove(self):
        '''Unregister the per-frame update callback and stop tracking.
        '''
        logic.getCurrentScene().pre_draw.remove(self.update)

    def update(self):
        '''Per-frame update called via ``pre_draw``.

        Calls the selected rotation function to orient ``game_object`` toward
        ``target``.  Does nothing when no rotation function is set.
        '''
        if self.rotate_func:
            self.rotate_func(self.game_object, self.target, self.front, self.speed)


class ULTrackTo(TrackTo):
    '''[DEPRECATED] Use :class:`TrackTo` instead.'''
    _deprecated = True


class Spring():
    '''Spring physics constraint connecting two objects or points.

    The two endpoints are pulled toward each other when the spring is
    stretched beyond its rest ``distance``.  Optionally they are also pushed
    apart when the spring is compressed (``use_push=True``).  The spring can
    be set to break automatically when the force exceeds ``break_threshold``
    (``use_breaking=True``).  A debug line can be drawn each frame
    (``visualize=True``) and an optional curve object can be deformed to
    follow the spring (``curve``).

    :param origin: First connection point of the spring (``GameObject`` or
        coordinate sequence).
    :param target: Second connection point of the spring (``GameObject`` or
        coordinate sequence).
    :param rigid_body_origin: Object to receive impulses at the origin end.
        Defaults to ``origin`` when not provided.
    :param rigid_body_target: Object to receive impulses at the target end.
        Defaults to ``target`` when not provided.
    :param stiffness: Spring stiffness constant — scales the force produced
        per unit of displacement from the rest distance.
    :param max_force: Upper bound on the spring force per frame.  A value of
        ``-1`` (default) disables the cap.
    :param distance: Rest length of the spring.  Defaults to the current
        distance between ``origin`` and ``target`` at construction time.
    :param use_push: When ``True``, also apply a repulsive force when the
        spring is compressed below the rest distance.
    :param use_breaking: When ``True``, remove the spring from ``pre_draw``
        once the computed force exceeds ``break_threshold``.
    :param break_threshold: Force threshold at which the spring breaks when
        ``use_breaking`` is enabled.
    :param curve: Optional curve object whose control points are repositioned
        each frame to follow the spring endpoints.
    :param visualize: When ``True``, draw a debug line between the endpoints
        each frame, coloured by the current force magnitude.
    '''

    _deprecated = False

    def __init__(
        self,
        origin: GameObject,
        target: GameObject,
        rigid_body_origin: GameObject = None,
        rigid_body_target: GameObject = None,
        stiffness: float = 1,
        max_force: float = -1,
        distance: float = None,
        use_push: bool = False,
        use_breaking: bool = False,
        break_threshold: float = 1,
        curve: GameObject or None = None,
        visualize: bool = False
    ) -> None:
        '''Initialise the spring, compute the rest distance, run an initial
        update, and register the per-frame callback.

        If ``use_breaking`` is ``True`` and the initial distance already
        exceeds ``distance``, the spring is not registered and never fires.

        :param origin: First endpoint — ``GameObject`` or coordinate sequence
            converted to ``Vector``.
        :param target: Second endpoint — ``GameObject`` or coordinate sequence
            converted to ``Vector``.
        :param rigid_body_origin: Rigid body to impulse at the origin end;
            falls back to ``origin``.
        :param rigid_body_target: Rigid body to impulse at the target end;
            falls back to ``target``.
        :param stiffness: Force-per-unit-displacement constant.
        :param max_force: Maximum force magnitude.  ``-1`` means unlimited.
        :param distance: Explicit rest length.  When ``None`` the distance
            between ``origin`` and ``target`` at construction time is used.
        :param use_push: Enable repulsive force when compressed.
        :param use_breaking: Automatically remove the spring when force
            exceeds ``break_threshold``.
        :param break_threshold: Force at which the spring breaks.
        :param curve: Curve object to deform along the spring each frame.
        :param visualize: Draw a debug line between the endpoints each frame.
        '''
        if self._deprecated:
            console.warning('ULSpring class will be renamed to "Spring" in future releases!')
        self.force = 0
        if isinstance(origin, tuple) or isinstance(origin, list):
            origin = Vector((origin))
        self.origin = origin
        if isinstance(target, tuple) or isinstance(target, list):
            target = Vector((target))
        self.target = target
        self.use_push = use_push
        self.rigid_body_origin = rigid_body_origin if rigid_body_origin else origin
        self.rigid_body_target = rigid_body_target if rigid_body_target else target
        self.stiffness = stiffness
        self.max_force = max_force
        self.use_breaking = use_breaking
        self.break_threshold = break_threshold
        self.visualize = visualize
        obj_dist = origin.getDistanceTo(target)
        self.distance = distance if distance is not None else obj_dist
        self.curve = curve
        if not use_breaking or self.distance >= obj_dist:
            self.update()
            logic.getCurrentScene().pre_draw.append(self.update)

    @property
    def points(self):
        '''Current world positions of the two spring endpoints.

        Read-only.  Returns ``[origin.worldPosition, target.worldPosition]``.

        :returns: A list of two ``Vector`` objects.
        '''
        return [self.origin.worldPosition, self.target.worldPosition]

    @points.setter
    def points(self, val):
        console.debug("Attribute 'points' is read-only")

    @property
    def active(self):
        '''Whether the spring is currently exerting a non-zero force.

        Read-only.  ``True`` when ``self.force != 0``.

        :returns: ``True`` if the spring force is non-zero, ``False`` otherwise.
        '''
        return self.force != 0

    @active.setter
    def active(self, val):
        console.debug("Attribute 'active' is read-only")

    def remove(self):
        '''Unregister the per-frame update callback and deactivate the spring.
        '''
        pre_draw = logic.getCurrentScene().pre_draw
        if self.update in pre_draw:
            pre_draw.remove(self.update)

    def update(self):
        '''Per-frame update called via ``pre_draw``.

        Computes ``force = (current_distance - rest_distance) * stiffness``,
        then optionally clamps it to ``max_force`` and suppresses negative
        (compressive) force when ``use_push`` is ``False``.  If
        ``use_breaking`` is enabled and ``force`` exceeds ``break_threshold``
        the spring removes itself and returns immediately.

        When ``visualize`` is ``True``, a debug line is drawn between the
        endpoints coloured by force magnitude.  When ``curve`` is set, its
        control points are updated to match :attr:`points`.  Finally, impulses
        proportional to ``force`` are applied to ``rigid_body_origin`` (toward
        the target) and ``rigid_body_target`` (toward the origin), provided
        each has a valid ``blenderObject`` with mesh data.
        '''
        o = self.origin
        t = self.target
        force = (o.getDistanceTo(t) - self.distance) * self.stiffness
        if self.max_force >= 0 and force > self.max_force:
            force = self.max_force
        if not self.use_push:
            force = force if force >= 0 else 0
        if self.use_breaking and force > self.break_threshold:
            logic.getCurrentScene().pre_draw.remove(self.update)
            return
        if self.visualize:
            start = getattr(o, 'worldPosition', o)
            end = getattr(t, 'worldPosition', t)
            render.drawLine(
                start,
                end,
                # [1, 1-abs(power), 1-abs(power)]
                [abs(force), 0, 1-abs(force)]
            )
        self.force = force
        if self.curve:
            set_curve_points(self.curve, self.points)
        rbo = self.rigid_body_origin
        rbt = self.rigid_body_target
        if hasattr(rbo, 'blenderObject') and rbo.blenderObject.data:
            rbo.applyImpulse(o.worldPosition, get_direction(o, t) * force)
        if hasattr(rbt, 'blenderObject') and rbt.blenderObject.data:
            rbt.applyImpulse(o.worldPosition, get_direction(t, o) * force)


class ULSpring(Spring):
    '''[DEPRECATED] Use :class:`Spring` instead.'''
    _deprecated = True

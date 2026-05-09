'''Game object utilities for uplogic: rotation helpers, curve creation and manipulation, a ``GameObject`` wrapper base class, and object-spawning helpers.
'''
from bge import logic
from bge.types import KX_GameObject
import bpy
from bpy.types import Material, Object
from .errors import LogicControllerNotSupportedError
from .constants import FRONT_AXIS_VECTOR_SIGNED
import math
from .math import project_vector3
from .math import clamp
from .math import get_local
from .math import rotate2d
from .math import rotate3d
from .math import rotate_by_axis
from ..events import schedule
from mathutils import Vector, Matrix, Euler
from math import degrees
from math import radians
from .collections import assign
from uplogic import console


def xrot_to(
    rotating_object,
    target_pos,
    front_axis_code=1,
    factor=1
):
    '''Rotate *rotating_object* around its local X-axis to face *target_pos*.

    Projects the direction to *target_pos* onto the object's local Y-Z plane,
    then computes the signed angle between that projection and the configured
    front direction and applies it as a local-space rotation.

    :param rotating_object: The ``KX_GameObject`` to rotate.
    :param target_pos: World-space position the object should face.
    :param front_axis_code: Integer code selecting the front axis direction
        (matches constants in ``FRONT_AXIS_VECTOR_SIGNED``). Default is ``1``.
    :param factor: Fraction of the computed angle to apply each call,
        allowing gradual interpolation. Default is ``1`` (instant).
    '''
    local = get_local(rotating_object, target_pos)
    front = Vector((1, 0)) if front_axis_code in [1, 4] else Vector((0, 1))
    if front_axis_code > 2:
        front.negate()
    angle = Vector((local.y, local.z))
    if angle.length < .001:
        return
    angle = angle.angle_signed(front)
    rotating_object.applyRotation((angle*factor, 0, 0), True)


def yrot_to(
    rotating_object,
    target_pos,
    front_axis_code=1,
    factor=1
):
    '''Rotate *rotating_object* around its local Y-axis to face *target_pos*.

    Projects the direction to *target_pos* onto the object's local X-Z plane,
    then computes the signed angle between that projection and the configured
    front direction and applies it as a local-space rotation.

    :param rotating_object: The ``KX_GameObject`` to rotate.
    :param target_pos: World-space position the object should face.
    :param front_axis_code: Integer code selecting the front axis direction
        (matches constants in ``FRONT_AXIS_VECTOR_SIGNED``). Default is ``1``.
    :param factor: Fraction of the computed angle to apply each call,
        allowing gradual interpolation. Default is ``1`` (instant).
    '''
    local = get_local(rotating_object, target_pos)
    front = Vector((1, 0)) if front_axis_code in [0, 3] else Vector((0, 1))
    if front_axis_code > 2:
        front.negate()
    angle = Vector((local.x, local.z))
    if angle.length < .001:
        return
    angle = angle.angle_signed(front)
    rotating_object.applyRotation((0, angle*factor, 0), True)


def zrot_to(
    rotating_object,
    target_pos,
    front_axis_code=1,
    factor=1
):
    '''Rotate *rotating_object* around its local Z-axis to face *target_pos*.

    Projects the direction to *target_pos* onto the object's local X-Y plane,
    then computes the signed angle between that projection and the configured
    front direction and applies it as a local-space rotation.

    :param rotating_object: The ``KX_GameObject`` to rotate.
    :param target_pos: World-space position the object should face.
    :param front_axis_code: Integer code selecting the front axis direction
        (matches constants in ``FRONT_AXIS_VECTOR_SIGNED``). Default is ``1``.
    :param factor: Fraction of the computed angle to apply each call,
        allowing gradual interpolation. Default is ``1`` (instant).
    '''
    local = get_local(rotating_object, target_pos)
    front = Vector((1, 0)) if front_axis_code in [0, 3] else Vector((0, 1))
    if front_axis_code > 2:
        front.negate()
    angle = Vector((local.x, local.y))
    if angle.length < .001:
        return
    angle = angle.angle_signed(front)
    rotating_object.applyRotation((0, 0, angle*factor), True)


def rotate_to(
    object: KX_GameObject,
    target: Vector,
    rotation_axis: int = 2,
    front_axis: int = 1,
    factor:float = 1
):
    '''Rotate an object around a chosen local axis to face a target point.

    Dispatches to :func:`xrot_to`, :func:`yrot_to`, or :func:`zrot_to`
    depending on *rotation_axis*. When *rotation_axis* equals *front_axis*
    (after normalising negative-direction codes) the function is a no-op, as
    rotating around the axis that already points at the target is undefined.

    :param object: The ``KX_GameObject`` to rotate.
    :param target: World-space position the object should face.
    :param rotation_axis: Local axis around which to rotate: ``0`` = X,
        ``1`` = Y, ``2`` = Z. Default is ``2``.
    :param front_axis: Integer code identifying the object's current forward
        direction (matches ``FRONT_AXIS_VECTOR_SIGNED``). Default is ``1``.
    :param factor: Fraction of the computed angle to apply each call.
        Default is ``1`` (instant).
    '''
    front = front_axis
    target = Vector(target)
    if front > 2:
        front -= 3
    if rotation_axis == front:
        return
    if rotation_axis == 0:
        xrot_to(
            object,
            target,
            front_axis,
            factor
        )
    elif rotation_axis == 1:
        yrot_to(
            object,
            target,
            front_axis,
            factor
        )
    elif rotation_axis == 2:
        zrot_to(
            object,
            target,
            front_axis,
            factor
        )


def move_to(game_object: KX_GameObject, target: Vector, speed: float, stop_distance=0):
    '''Move *game_object* toward *target* by *speed* units per tick.

    When the remaining distance is less than ``speed + stop_distance`` the
    object is snapped to the offset position (``target + direction *
    stop_distance``) and the function returns ``True`` to signal arrival.

    :param game_object: The ``KX_GameObject`` to move.
    :param target: Destination world-space position as a ``Vector``.
    :param speed: Distance to travel per logic tick.
    :param stop_distance: Minimum distance at which the object is considered
        to have arrived and is snapped into place. Default is ``0``.
    :returns: ``True`` when the object has reached (or is within
        *stop_distance* of) *target*, otherwise ``None``.
    '''
    distance = (game_object.worldPosition - target)
    direction = distance.normalized()
    if distance.length < speed + stop_distance:
        game_object.worldPosition = target + direction * stop_distance
        return True
    game_object.worldPosition -= direction * speed


def _move_to(
    moving_object,
    destination_point,
    speed,
    time_per_frame,
    dynamic,
    distance,
    snap=True
):
    '''Internal movement implementation supporting both dynamic and static objects.

    Not intended for direct use; call :func:`move_to` instead.

    For dynamic objects the horizontal velocity is set directly on the physics
    body while preserving the current Z velocity. For static objects the
    world position is incremented by a frame-time-scaled displacement.

    :param moving_object: The ``KX_GameObject`` to move.
    :param destination_point: Target world-space ``Vector``.
    :param speed: Movement speed in units per second.
    :param time_per_frame: Elapsed time for the current frame (delta time).
    :param dynamic: When ``True``, moves by setting ``worldLinearVelocity``
        (physics body); when ``False``, moves by directly updating
        ``worldPosition``.
    :param distance: Arrival threshold; the object stops when it is within
        this distance of *destination_point*.
    :param snap: When ``True`` and the object has arrived, snaps it exactly
        onto *destination_point*. Default is ``True``.
    :returns: ``True`` when the object has arrived, ``False`` otherwise.
    '''
    if dynamic:
        direction = (
            destination_point -
            moving_object.worldPosition)
        dst = direction.length
        if(dst <= distance):
            if snap:
                moving_object.worldPosition = destination_point
            return True
        direction.z = 0
        direction.normalize()
        velocity = direction * speed
        velocity.z = moving_object.worldLinearVelocity.z
        moving_object.worldLinearVelocity = velocity
        return False
    else:
        direction = (
            destination_point -
            moving_object.worldPosition
            )
        dst = direction.length
        if(dst <= distance):
            if snap:
                moving_object.worldPosition = destination_point
            return True
        direction.normalize()
        displacement = speed * time_per_frame
        motion = direction * displacement
        moving_object.worldPosition += motion
        return False


def controller_brick_status(owner, controller_name):
    '''Evaluate the logic state of a named BGE controller brick.

    Reads the controller type (AND / OR / NAND / NOR / XOR / XNOR) from the
    Blender game data and applies the corresponding boolean reduction over the
    ``positive`` states of all connected sensors.

    :param owner: The ``KX_GameObject`` that owns the controller.
    :param controller_name: String name of the controller brick to evaluate.
    :returns: ``True`` if the controller's logic condition is satisfied,
        ``False`` otherwise.
    :raises LogicControllerNotSupportedError: If the controller type is not
        one of the six supported logic types.
    '''
    cont = owner.controllers[controller_name]
    state = (
        owner
        .blenderObject
        .game
        .controllers[controller_name]
        .type
    )
    if not cont.sensors:
        return False
    elif state == 'LOGIC_AND':
        return False not in [sens.positive for sens in cont.sensors]
    elif state == 'LOGIC_OR':
        return True in [sens.positive for sens in cont.sensors]
    elif state == 'LOGIC_NAND':
        return False in [sens.positive for sens in cont.sensors]
    elif state == 'LOGIC_NOR':
        return True not in [sens.positive for sens in cont.sensors]
    elif state == 'LOGIC_XOR':
        return [
            sens.positive
            for sens in
            cont.sensors
        ].count(True) % 2 != 0
    elif state == 'LOGIC_XNOR':
        check = cont.sensors[0].positive
        return False not in [
            sens.positive == check
            for sens in
            cont.sensors
        ]
    else:
        raise LogicControllerNotSupportedError


class ControllerBrick(tuple):
    '''Named-accessor wrapper around a controller result tuple.

    Inherits from ``tuple`` so the underlying data can be iterated or indexed
    like a plain sequence. The four positional elements are exposed as
    read-only properties for convenient attribute access.

    Element layout: ``(brick, positive, sensors, actuators)``.
    '''

    @property
    def brick(self):
        '''The raw BGE controller object (``self[0]``).'''
        return self[0]

    @property
    def name(self):
        '''Name of the controller brick (``self[0].name``).'''
        return self[0].name

    @property
    def positive(self):
        '''Evaluated boolean logic state of the controller (``self[1]``).'''
        return self[1]

    @property
    def sensors(self):
        '''List of sensors connected to the controller (``self[2]``).'''
        return self[2]

    @property
    def actuators(self):
        '''List of actuators connected to the controller (``self[3]``).'''
        return self[3]


def controller_brick(owner, controller_name):
    '''Return a :class:`ControllerBrick` for a named BGE controller.

    Like :func:`controller_brick_status` but packages the result together with
    the controller object and its sensor / actuator lists into a
    :class:`ControllerBrick` tuple for structured access.

    :param owner: The ``KX_GameObject`` that owns the controller.
    :param controller_name: String name of the controller brick to evaluate.
    :returns: A :class:`ControllerBrick` containing
        ``(controller, evaluated_state, sensors, actuators)``.
    :raises LogicControllerNotSupportedError: If the controller type is not
        one of the six supported logic types.
    '''
    cont = owner.controllers[controller_name]
    state = (
        owner
        .blenderObject
        .game
        .controllers[controller_name]
        .type
    )
    if not cont.sensors:
        return ControllerBrick([cont, False, cont.sensors, cont.actuators])
    elif state == 'LOGIC_AND':
        return ControllerBrick([cont, False not in [sens.positive for sens in cont.sensors], cont.sensors, cont.actuators])
    elif state == 'LOGIC_OR':
        return ControllerBrick([cont, True in [sens.positive for sens in cont.sensors], cont.sensors, cont.actuators])
    elif state == 'LOGIC_NAND':
        return ControllerBrick([cont, False in [sens.positive for sens in cont.sensors], cont.sensors, cont.actuators])
    elif state == 'LOGIC_NOR':
        return ControllerBrick([cont, True not in [sens.positive for sens in cont.sensors], cont.sensors, cont.actuators])
    elif state == 'LOGIC_XOR':
        return ControllerBrick([cont, [
            sens.positive
            for sens in
            cont.sensors
        ].count(True) % 2 != 0, cont.sensors, cont.actuators])
    elif state == 'LOGIC_XNOR':
        check = cont.sensors[0].positive
        return ControllerBrick([cont, False not in [
            sens.positive == check
            for sens in
            cont.sensors
        ], cont.sensors, cont.actuators])
    else:
        raise LogicControllerNotSupportedError


def create_curve(
    name: str,
    bevel_depth: float = 0.0,
    dimensions: int = 3,
    material: str or Material = None,
    collection: str = None
) -> KX_GameObject:
    '''Create a ``KX_GameObject`` containing a ``bpy.types.Curve`` object.

    A new Blender curve data-block and object are created, optionally given a
    material and linked into *collection*, then converted to a live
    ``KX_GameObject`` via ``logic.getCurrentScene().convertBlenderObject``.

    :param name: Name for both the curve data-block and the new object.
    :param bevel_depth: Diameter of the bevel geometry added along the spline.
        ``0.0`` produces a bare spline with no mesh thickness. Default is
        ``0.0``.
    :param dimensions: Coordinate space for the curve: ``2`` for 2-D or ``3``
        for 3-D. Default is ``3``.
    :param material: Material to assign to the bevel geometry. Accepts a
        material name string or a ``bpy.types.Material`` instance. Pass
        ``None`` to leave the curve unshaded. Default is ``None``.
    :param collection: Collection into which the new object is linked. Accepts
        a collection name string. Pass ``None`` to link into the active scene
        collection. Default is ``None``.
    :returns: The newly created ``KX_GameObject``.
    '''
    bcurve = bpy.data.curves.new(name, 'CURVE')
    bcurve.bevel_depth = bevel_depth
    bcurve.dimensions = f'{dimensions}D'
    bobj = bpy.data.objects.new(name, bcurve)
    if material:
        if isinstance(material, str):
            bobj.data.materials.append(bpy.data.materials[material])
        elif isinstance(material, Material):
            bobj.data.materials.append(material)
    if collection:
        if isinstance(collection, str):
            collection = bpy.data.collections.get(collection, bpy.context.scene.collection)
    elif collection is None:
        collection = bpy.context.scene.collection
    collection.objects.link(bobj)
    game_obj = logic.getCurrentScene().convertBlenderObject(bobj)
    return game_obj


def set_curve_points(
    curve: KX_GameObject,
    points: list,
    loop: bool = False,
    type: str = 'POLY'
) -> None:
    '''Replace all splines on *curve* with a single new spline built from *points*.

    All existing splines are removed before the new one is added. Each point
    in *points* is converted from world space into the curve's local space by
    subtracting the curve's current ``worldPosition``.

    :param curve: ``KX_GameObject`` whose underlying ``bpy.types.Curve`` data
        will be modified.
    :param points: Sequence of 3-component positions (world space) that define
        the new spline.
    :param loop: When ``True``, the spline is closed (cyclic). Default is
        ``False``.
    :param type: Spline interpolation type passed to
        ``bpy.types.Curve.splines.new()``, e.g. ``'POLY'``, ``'BEZIER'``, or
        ``'NURBS'``. Default is ``'POLY'``.
    '''
    bcurve = curve.blenderObject.data
    for spline in bcurve.splines:
        bcurve.splines.remove(spline)
    spline = bcurve.splines.new(type)
    spline.use_cyclic_u = loop
    pos = curve.worldPosition

    spline.points.add(len(points)-1)
    for p, new_co in zip(spline.points, points):
        p.co = ([
            new_co[0] - pos.x,
            new_co[1] - pos.y,
            new_co[2] - pos.z
        ] + [1.0])


class GameObject:
    '''Thin wrapper around a ``KX_GameObject`` exposing common transform and
    hierarchy attributes as plain Python properties.

    All property reads and writes delegate to the underlying
    ``self.game_object`` so that this class can be used as a drop-in
    substitute wherever a ``KX_GameObject`` is expected via composition.

    :param game_object: The ``KX_GameObject`` instance to wrap.
    '''

    def __init__(self, game_object: KX_GameObject) -> None:
        '''Initialise the wrapper and cache the Blender mesh data reference.

        :param game_object: The ``KX_GameObject`` to wrap.
        '''
        self.game_object: KX_GameObject = game_object
        self.data = self.game_object.blenderObject.data

    @property
    def blenderObject(self) -> Object:
        '''The underlying ``bpy.types.Object`` linked to this game object.'''
        return self.game_object.blenderObject

    @property
    def parent(self) -> KX_GameObject:
        '''Parent ``KX_GameObject`` in the scene hierarchy, or ``None``.'''
        return self.game_object.parent

    @parent.setter
    def parent(self, val: KX_GameObject):
        '''Set the parent by calling ``setParent`` on the wrapped object.

        :param val: New parent ``KX_GameObject``.
        '''
        self.game_object.setParent(val)

    def set_parent(self, parent):
        '''Set the parent ``KX_GameObject`` explicitly.

        :param parent: New parent ``KX_GameObject``.
        '''
        self.game_object.setParent(parent)

    @property
    def children(self):
        '''Direct children of this game object.'''
        return self.game_object.children

    @property
    def children_recursive(self):
        '''All descendants of this game object (recursive).'''
        return self.game_object.childrenRecursive

    @property
    def mass(self):
        '''Physics mass of the object. Returns ``0`` if not applicable.'''
        return getattr(self.game_object, 'mass', 0)

    @mass.setter
    def mass(self, val):
        self.game_object.mass = val

    @property
    def worldPosition(self) -> Vector:
        '''World-space position as a ``Vector``.'''
        return self.game_object.worldPosition

    @worldPosition.setter
    def worldPosition(self, val: Vector):
        self.game_object.worldPosition = val

    @property
    def localPosition(self) -> Vector:
        '''Position relative to the parent object as a ``Vector``.'''
        return self.game_object.localPosition

    @localPosition.setter
    def localPosition(self, val: Vector):
        self.game_object.localPosition = val

    @property
    def worldOrientation(self) -> Matrix:
        '''World-space orientation as a 3x3 rotation ``Matrix``.'''
        return self.game_object.worldOrientation

    @worldOrientation.setter
    def worldOrientation(self, val: Matrix):
        self.game_object.worldOrientation = val

    @property
    def localOrientation(self) -> Matrix:
        '''Orientation relative to the parent as a 3x3 rotation ``Matrix``.'''
        return self.game_object.localOrientation

    @localOrientation.setter
    def localOrientation(self, val: Matrix):
        self.game_object.localOrientation = val

    @property
    def worldScale(self) -> Vector:
        '''World-space scale as a ``Vector``.'''
        return self.game_object.worldScale

    @worldScale.setter
    def worldScale(self, val: Vector):
        self.game_object.worldScale = val

    @property
    def localScale(self) -> Vector:
        '''Scale relative to the parent as a ``Vector``.'''
        return self.game_object.localScale

    @localScale.setter
    def localScale(self, val: Vector):
        self.game_object.localScale = val

    @property
    def worldLinearVelocity(self) -> Vector:
        '''Linear velocity in world space as a ``Vector``.'''
        return self.game_object.worldLinearVelocity

    @worldLinearVelocity.setter
    def worldLinearVelocity(self, val: Vector):
        self.game_object.worldLinearVelocity = val

    @property
    def localLinearVelocity(self) -> Vector:
        '''Linear velocity in local (object) space as a ``Vector``.'''
        return self.game_object.localLinearVelocity

    @localLinearVelocity.setter
    def localLinearVelocity(self, val: Vector):
        self.game_object.localLinearVelocity = val

    @property
    def worldAngularVelocity(self) -> Vector:
        '''Angular velocity in world space as a ``Vector``.'''
        return self.game_object.worldAngularVelocity

    @worldAngularVelocity.setter
    def worldAngularVelocity(self, val: Vector):
        self.game_object.worldAngularVelocity = val

    @property
    def localAngularVelocity(self) -> Vector:
        '''Angular velocity in local (object) space as a ``Vector``.'''
        return self.game_object.localAngularVelocity

    @localAngularVelocity.setter
    def localAngularVelocity(self, val: Vector):
        self.game_object.localAngularVelocity = val

    @property
    def worldTransform(self) -> Matrix:
        '''World-space 4x4 transform ``Matrix`` (position + orientation + scale).'''
        return self.game_object.worldTransform

    @worldTransform.setter
    def worldTransform(self, val: Matrix):
        self.game_object.worldTransform = val

    def move_to(self, target, speed):
        '''Move this object toward *target* by *speed* per tick.

        Delegates to the module-level :func:`move_to` function.

        :param target: Destination world-space position as a ``Vector``.
        :param speed: Distance to travel per logic tick.
        :returns: ``True`` when the object has arrived at *target*.
        '''
        return move_to(self, target, speed)


def get_curve_length(curve: KX_GameObject):
    '''Return the total arc length of all splines on *curve*.

    Evaluates the dependency graph to obtain the final (modifier-applied) mesh
    data and sums ``calc_length()`` over every spline.

    :param curve: ``KX_GameObject`` whose underlying ``bpy.types.Curve`` data
        is measured.
    :returns: Total arc length as a ``float``.
    '''
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return sum(s.calc_length() for s in curve.blenderObject.evaluated_get(depsgraph).data.splines)


def evaluate_curve(curve: KX_GameObject, factor: float = .5):
    '''Return the world-space position on *curve* at the given *factor*.

    Creates a temporary empty object, attaches a ``FOLLOW_PATH`` constraint
    targeting *curve*, advances ``eval_time`` to ``path_duration * factor``,
    forces a view-layer update, reads the resulting local matrix, then cleans
    up the temporary object and restores the original ``eval_time``.

    :param curve: ``KX_GameObject`` whose path is evaluated.
    :param factor: Normalised position along the curve: ``0.0`` = start,
        ``1.0`` = end. Default is ``0.5``.
    :returns: World-space ``Vector`` at the requested position.
    '''
    eval_obj = bpy.data.objects.new(f'{curve.name}_eval_obj', object_data=None)
    bpy.context.collection.objects.link(eval_obj)
    bobj = curve.blenderObject
    const = eval_obj.constraints.new('FOLLOW_PATH')
    const.target = bobj
    const.use_curve_follow = True
    time = bobj.data.eval_time
    bobj.data.eval_time = bobj.data.path_duration * factor
    bpy.context.view_layer.update()
    matrix = eval_obj.matrix_local
    bpy.data.objects.remove(eval_obj)
    bobj.data.eval_time = time
    return Vector((matrix[0][3], matrix[1][3], matrix[2][3]))


class Curve(GameObject):
    '''High-level wrapper for creating and manipulating BGE curve objects.

    When *name* is a string a new ``bpy.types.Curve`` object is created via
    :func:`create_curve` and converted to a ``KX_GameObject``. When *name* is
    already a ``KX_GameObject`` the existing object is wrapped instead.

    :param name: Name string for a new curve, or an existing ``KX_GameObject``
        to wrap.
    :param bevel_depth: Diameter of the bevel geometry along the spline.
        Default is ``0.0``.
    :param dimensions: Coordinate space: ``2`` for 2-D or ``3`` for 3-D.
        Default is ``3``.
    :param material: Material for bevel geometry — a name string or
        ``bpy.types.Material`` instance. Default is ``None``.
    :param collection: Collection name to link the new object into. Default is
        ``None`` (active scene collection).
    :param loop: When ``True`` the spline is closed (cyclic). Default is
        ``False``.
    :param type: Spline type, e.g. ``'POLY'``, ``'BEZIER'``, ``'NURBS'``.
        Default is ``'POLY'``.
    :param use_evaluate: When ``True``, the evaluation helper object is kept
        alive between calls to :meth:`evaluate` rather than being recreated
        each time. Default is ``False``.
    '''

    _deprecated = False

    def __init__(
        self,
        name: str,
        bevel_depth: float = 0.0,
        dimensions: int = 3,
        material: str or Material = None,
        collection: str = None,
        loop: bool = False,
        type: str = 'POLY',
        use_evaluate = False
    ) -> None:
        self._array_object = None
        if self._deprecated:
            console.warning('[UPLOGIC] ULCurve class will be renamed to "Curve" in future releases!')
        self.type = type
        self._loop = loop
        self.use_evaluate = use_evaluate
        if isinstance(name, KX_GameObject):
            self.game_object = name
            # bcurve: bpy.types.Curve = self.game_object.blenderObject.data
            # bcurve.bevel_depth = bevel_depth
            # bcurve.dimensions = f'{dimensions}D'
            if isinstance(material, str):
                self.blenderObject.data.materials.append(bpy.data.materials[material])
            elif isinstance(material, Material):
                self.blenderObject.data.materials.append(material)
        else:
            self.game_object = create_curve(
                name=name,
                bevel_depth=bevel_depth,
                dimensions=dimensions,
                material=material,
                collection=collection
            )
        self.data = self.game_object.blenderObject.data
        self._style = 'line'
        self.bevel_depth = bevel_depth
        self.dash_length = 1
        self.style_spacing = .5

    @property
    def eval_obj(self):
        '''Persistent evaluation helper object used by :meth:`evaluate`.

        Creates and links a new empty with a ``FOLLOW_PATH`` constraint the
        first time it is accessed; subsequent calls return the cached object.
        '''
        eval_obj = bpy.data.objects.get(f'{self.name}_eval_obj', None)
        if eval_obj is None:
            eval_obj = bpy.data.objects.new(f'{self.name}_eval_obj', object_data=None)
            bpy.context.collection.objects.link(eval_obj)
            const = eval_obj.constraints.new('FOLLOW_PATH')
            const.target = self.blenderObject
            const.use_curve_follow = True
        return eval_obj

    def _create_dots(self):
        '''Build a UV-sphere array object that renders dots along the curve.'''
        bpy.context.scene.cursor.location = (0, 0, 0)
        self.data.twist_mode = 'Z_UP'
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=self.bevel_depth)
        bpy.ops.object.shade_smooth()
        dot = bpy.context.object
        dot.location = (self.bevel_depth * .5, 0, 0)
        bpy.ops.object.transform_apply(location=True, scale=False, properties=False, isolate_users=False)
        dot.parent = self.blenderObject
        self._make_array()

    def _create_dashes(self):
        '''Build a cylinder array object that renders dashes along the curve.'''
        bpy.context.scene.cursor.location = (0, 0, 0)
        self.data.twist_mode = 'Z_UP'
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=self.bevel_depth, rotation=(0, math.pi * .5, 0), depth=self.dash_length)
        bpy.ops.object.shade_smooth()
        dot = bpy.context.object
        dot.location = (self.dash_length * .5, 0, 0)
        bpy.ops.object.transform_apply(location=True, scale=False, properties=False, isolate_users=False)
        dot.parent = self.blenderObject
        self._make_array()

    def _remove_style(self):
        '''Remove the current array style object and restore plain bevel rendering.'''
        if self._array_object is not None:
            bpy.data.objects.remove(self._array_object)
        self._array_object = None
        self.data.bevel_depth = self.bevel_depth

    def _make_array(self):
        '''Attach ``ARRAY`` and ``CURVE`` modifiers to the active style object.'''
        self._remove_style()
        dot = bpy.context.object
        if self.material:
            dot.data.materials.append(self.material)
        self.data.bevel_depth = 0.
        dot.location = self.worldPosition
        mod: bpy.types.ArrayModifier = dot.modifiers.new('Array', "ARRAY")
        mod.fit_type = "FIT_CURVE"
        mod.curve = self.blenderObject
        mod.use_constant_offset = True
        # mod.use_relative_offset = False
        mod.constant_offset_displace.x = 1 + self.style_spacing
        cmod: bpy.types.CurveModifier = dot.modifiers.new('Array', "CURVE")
        cmod.object = self.blenderObject
        self._array_object = dot

    def _restyle(self):
        '''Rebuild the style geometry to match the current :attr:`style` value.'''
        if self.style == "dots":
            self._create_dots()
        if self.style == "dashes":
            self._create_dashes()
        if self.style == 'line':
            # XXX: Investigate bevel_depth set to 0 if setting style attributes after setting radius
            self._remove_style()

    @property
    def style_spacing(self):
        '''Gap between repeated style elements (dots or dashes) along the curve.'''
        return self._style_spacing

    @style_spacing.setter
    def style_spacing(self, val):
        self._style_spacing = val
        self._restyle()

    @property
    def style(self):
        '''Rendering style of the curve: ``'line'``, ``'dots'``, or ``'dashes'``.'''
        return self._style

    @style.setter
    def style(self, val):
        if val == self.style:
            return
        self._style = val
        self._restyle()

    @property
    def dash_length(self):
        '''Length of each dash element when :attr:`style` is ``'dashes'``.'''
        return self._dash_length

    @dash_length.setter
    def dash_length(self, val):
        self._dash_length = val
        self._restyle()

    @property
    def material(self):
        '''First material slot of the curve's Blender object, or ``None``.'''
        if len(self.blenderObject.data.materials):
            return self.blenderObject.data.materials[0]

    # @material.setter
    # def style(self, val):
    #     if val == self.style:
    #         return
    #     if val == "dots":
    #         self.
    #     self._style = val

    @property
    def name(self):
        '''Name of the underlying game object (read-only).'''
        return self.game_object.name

    @name.setter
    def name(self, val: str):
        console.debug('Curve.name is Read-Only!')

    @property
    def loop(self):
        '''Whether the curve spline is closed (cyclic).'''
        return self._loop

    @loop.setter
    def loop(self, val: bool):
        self._loop = val
        self.points = self.points

    @property
    def points(self):
        '''Control points of the first spline in global space.'''
        splines = self.data.splines
        return (
            splines[0].bezier_points if len(splines) > 0 else []
            if splines[0].type == 'BEZIER' else
            splines[0].points if len(splines) > 0 else []
        )

    @points.setter
    def points(self, val: list):
        if val != self.points:
            set_curve_points(self.game_object, val, loop=self.loop, type=self.type)

    @property
    def bevel_depth(self):
        '''Thickness of the curve geometry as a diameter value.'''
        return self._bevel_depth

    @bevel_depth.setter
    def bevel_depth(self, val):
        self._bevel_depth = val
        if self._array_object:
            if self.style == 'dots':
                self._create_dots()
            if self.style == 'dashes':
                self._create_dashes()
        else:
            self.data.bevel_depth = val

    @property
    def length(self):
        '''Total arc length of the curve (read-only).'''
        depsgraph = bpy.context.evaluated_depsgraph_get()
        return sum(s.calc_length() for s in self.blenderObject.evaluated_get(depsgraph).data.splines)

    @length.setter
    def length(self, val):
        console.debug('Curve.length is read-only!')

    @property
    def path_duration(self):
        '''Number of frames required to traverse the full path (``path_duration``).'''
        return self.blenderObject.data.path_duration

    @path_duration.setter
    def path_duration(self, val):
        self.data.path_duration = val

    @property
    def resolution(self):
        '''Curve resolution (``resolution_u``) controlling spline subdivision.'''
        return self.data.resolution_u

    @resolution.setter
    def resolution(self, val):
        self.data.resolution_u = int(val)

    @property
    def time(self):
        '''Current evaluation time (``eval_time``) along the curve path.'''
        return self.data.eval_time

    @time.setter
    def time(self, val):
        self.data.eval_time = val

    def evaluate(self, factor) -> Matrix:
        '''Return the world-space matrix on the curve at the given progress.

        Temporarily sets ``eval_time`` to ``path_duration * factor``, forces a
        view-layer update, reads the local matrix of the evaluation helper
        object, then restores the original ``eval_time``. The helper object is
        removed unless :attr:`use_evaluate` is ``True``.

        :param factor: Normalised position along the curve: ``0.0`` = start,
            ``1.0`` = end.
        :returns: Local-space ``Matrix`` of the evaluation helper at the
            requested position.
        '''
        time = self.blenderObject.data.eval_time
        eval_obj = self.eval_obj
        self.blenderObject.data.eval_time = self.path_duration * factor
        bpy.context.view_layer.update()
        matrix = eval_obj.matrix_local
        if not self.use_evaluate:
            bpy.data.objects.remove(eval_obj)
        self.blenderObject.data.eval_time = time
        return matrix


class ULCurve(Curve):
    '''[DEPRECATED] Use :class:`Curve` instead.'''
    _deprecated = True


class Mesh():
    '''Minimal wrapper around a ``bpy.types.Mesh`` for direct mesh data manipulation.

    :param mesh: The ``bpy.types.Mesh`` data-block to wrap.
    '''

    def __init__(self, mesh: bpy.types.Mesh):
        self.blenderMesh: bpy.types.Mesh = mesh

    def applyRotation(self, rotation, local=False):
        '''Transform the mesh vertex data by *rotation*.

        Converts *rotation* (a 3-component Euler angle sequence) to a 4x4
        matrix and passes it to ``bpy.types.Mesh.transform`` to permanently
        rotate the mesh geometry.

        :param rotation: Sequence of three Euler angles (radians) describing
            the rotation to apply.
        :param local: Unused; reserved for future local-space support.
        '''
        rot = Euler(rotation)
        self.blenderMesh.transform(
            rot.to_matrix().to_4x4()
        )


def add_object(name: str | KX_GameObject, ref: str | KX_GameObject = None, time = 0, dupli = False):
    '''Copy a Blender object and add it to the current BGE scene.

    The original object is looked up by name in ``bpy.data.objects``, a copy
    is made, the copy is linked into the scene collection, and then converted
    to a ``KX_GameObject``. Optionally the new object's world transform is
    matched to a reference object and/or its lifetime is capped.

    :param name: Name of the Blender object to copy, or an existing
        ``KX_GameObject`` whose name is used.
    :param ref: Optional reference object whose world transform is applied to
        the new object. Accepts a name string or a ``KX_GameObject``.
        Default is ``None``.
    :param time: If greater than ``0``, schedules ``endObject`` to be called
        after *time* seconds. Default is ``0``.
    :param dupli: When ``True``, the mesh data is also copied (full duplicate).
        When ``False``, the copy shares the original's mesh. Default is
        ``False``.
    :returns: The newly created ``KX_GameObject``, or ``None`` if the source
        object was not found.
    '''
    scene = logic.getCurrentScene()
    if isinstance(name, KX_GameObject):
        name = name.name
    obj = bpy.data.objects.get(name, None)
    if obj is None:
        return
    new_obj = obj.copy()
    new_obj.hide_viewport = False
    if dupli:
        new_obj.data = obj.data.copy()
    bpy.context.scene.collection.objects.link(new_obj)
    game_object = scene.convertBlenderObject(new_obj)
    if ref:
        if isinstance(ref, KX_GameObject):
            ref = ref.name
        ref_obj = scene.objects.get(ref, ref)
        game_object.worldTransform = ref_obj.worldTransform
    if time > 0:
        schedule(game_object.endObject, time)
    # game_object.name = name
    return game_object


def add_object_copy(name: str | KX_GameObject, position=Vector((0, 0, 0)), rotation=Vector((0, 0, 0)), scale=Vector((1, 1, 1))):
    '''Copy a Blender object and place it at an explicit world transform.

    Like :func:`add_object` but sets *position*, *rotation*, and *scale*
    directly on the new ``KX_GameObject`` instead of aligning to a reference
    object. The mesh data is shared with the original (no full duplicate).

    :param name: Name of the Blender object to copy.
    :param position: World-space position for the new object. Default is the
        origin ``(0, 0, 0)``.
    :param rotation: World-space orientation (Euler angles or matrix) for the
        new object. Default is no rotation ``(0, 0, 0)``.
    :param scale: World-space scale for the new object. Default is uniform
        scale ``(1, 1, 1)``.
    :returns: The newly created ``KX_GameObject``, or ``None`` if the source
        object was not found.
    '''
    orig_ob = bpy.data.objects.get(name, name)
    if orig_ob is None:
        return
    game_scene = logic.getCurrentScene()
    scene = bpy.data.scenes[game_scene.name]
    ob = orig_ob.copy()
    scene.collection.objects.link(ob)
    gobj = game_scene.convertBlenderObject(ob)
    gobj.worldPosition = position
    gobj.worldOrientation = rotation
    gobj.worldScale = scale
    return gobj


def add_object_from_mesh(name: str | KX_GameObject, position=Vector((0, 0, 0)), rotation=Vector((0, 0, 0)), scale=Vector((1, 1, 1))):
    '''Create a new Blender object that shares the named object's mesh data.

    Rather than copying the full object, a brand-new ``bpy.types.Object`` is
    created with the original's mesh data-block, giving a lightweight instance
    that does not duplicate mesh memory.

    :param name: Name of the source Blender object whose mesh data is reused.
    :param position: World-space position for the new object. Default is the
        origin ``(0, 0, 0)``.
    :param rotation: World-space orientation (Euler angles or matrix) for the
        new object. Default is no rotation ``(0, 0, 0)``.
    :param scale: World-space scale for the new object. Default is uniform
        scale ``(1, 1, 1)``.
    :returns: The newly created ``KX_GameObject``, or ``None`` if the source
        object was not found.
    '''
    orig_ob = bpy.data.objects.get(name, None)
    if orig_ob is None:
        return
    game_scene = logic.getCurrentScene()
    scene = bpy.data.scenes[game_scene.name]
    ob = bpy.data.objects.new(name, orig_ob.data)
    scene.collection.objects.link(ob)
    gobj = game_scene.convertBlenderObject(ob)
    gobj.worldPosition = position
    gobj.worldOrientation = rotation
    gobj.worldScale = scale
    return gobj

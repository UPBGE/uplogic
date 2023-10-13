from bge import logic
from bge.types import KX_GameObject
import bpy
from bpy.types import Material, Object
from .errors import LogicControllerNotSupportedError
from .constants import FRONT_AXIS_VECTOR_SIGNED
from .math import project_vector3
from .math import clamp
from .math import get_local
from mathutils import Vector, Matrix
from math import degrees


def xrot_to(
    rotating_object,
    target_pos,
    front_axis_code=1,
    factor=1
):
    local = get_local(rotating_object, target_pos)
    front = Vector((1, 0)) if front_axis_code == 1 else Vector((0, 1))
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
    local = get_local(rotating_object, target_pos)
    front = Vector((1, 0)) if front_axis_code == 0 else Vector((0, 1))
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
    local = get_local(rotating_object, target_pos)
    front = Vector((1, 0)) if front_axis_code == 0 else Vector((0, 1))
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
    """Rotate an object around a local axis towards a point"""
    front = front_axis
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


def move_to(
    moving_object,
    destination_point,
    speed,
    time_per_frame,
    dynamic,
    distance
):
    if dynamic:
        direction = (
            destination_point -
            moving_object.worldPosition)
        dst = direction.length
        if(dst <= distance):
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
            return True
        direction.normalize()
        displacement = speed * time_per_frame
        motion = direction * displacement
        moving_object.worldPosition += motion
        return False


def controller_brick_status(owner, controller_name):
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

    @property
    def brick(self):
        return self[0]

    @property
    def name(self):
        return self[0].name

    @property
    def positive(self):
        return self[1]

    @property
    def sensors(self):
        return self[2]

    @property
    def actuators(self):
        return self[3]


def controller_brick(owner, controller_name):
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
    """Create a `KX_GameObject` containing a `bpy.types.Curve` object.

    :param `name`: Name of the new `KX_GameObject`.
    :param `bevel_depth`: Define the "thickness" of the curve. This will add
    geometry along the spline.
    :param `dimensions`: Set the coordinate space in which to calculate the
    curve.
    :param `material`: The material to use for bevel geometry.
    :param `collection`: The collection to which to add the curve. Leave at
    `None` to use scene collection.
    """
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
    points: list
) -> None:
    """Set the curve points of a `KX_GameObject` containing a `bpy.types.Curve` object.

    :param `curve`: `KX_GameObject`
    :param `points`: A list of points to use for the curve.
    """
    bcurve = curve.blenderObject.data
    for spline in bcurve.splines:
        bcurve.splines.remove(spline)
    spline = bcurve.splines.new('POLY')
    pos = curve.worldPosition

    spline.points.add(len(points)-1)
    for p, new_co in zip(spline.points, points):
        p.co = ([
            new_co[0] - pos.x,
            new_co[1] - pos.y,
            new_co[2] - pos.z
        ] + [1.0])


class GameObject:

    def __init__(self) -> None:
        self.game_object: KX_GameObject

    @property
    def blenderObject(self) -> Object:
        return self.game_object.blenderObject

    @property
    def parent(self) -> KX_GameObject:
        return self.game_object.parent

    @parent.setter
    def parent(self, val: KX_GameObject):
        self.game_object.setParent(val)

    def set_parent(self, parent):
        self.game_object.setParent(parent)

    @property
    def worldPosition(self) -> Vector:
        return self.game_object.worldPosition

    @worldPosition.setter
    def worldPosition(self, val: Vector):
        self.game_object.worldPosition = val

    @property
    def localPosition(self) -> Vector:
        return self.game_object.localPosition

    @localPosition.setter
    def localPosition(self, val: Vector):
        self.game_object.localPosition = val

    @property
    def worldOrientation(self) -> Matrix:
        return self.game_object.worldOrientation

    @worldOrientation.setter
    def worldOrientation(self, val: Matrix):
        self.game_object.worldOrientation = val

    @property
    def localOrientation(self) -> Matrix:
        return self.game_object.localOrientation

    @localOrientation.setter
    def localOrientation(self, val: Matrix):
        self.game_object.localOrientation = val

    @property
    def worldScale(self) -> Vector:
        return self.game_object.worldScale

    @worldScale.setter
    def worldScale(self, val: Vector):
        self.game_object.worldScale = val

    @property
    def localScale(self) -> Vector:
        return self.game_object.localScale

    @localScale.setter
    def localScale(self, val: Vector):
        self.game_object.localScale = val

    @property
    def worldLinearVelocity(self) -> Vector:
        return self.game_object.worldLinearVelocity

    @worldLinearVelocity.setter
    def worldLinearVelocity(self, val: Vector):
        self.game_object.worldLinearVelocity = val

    @property
    def localLinearVelocity(self) -> Vector:
        return self.game_object.localLinearVelocity

    @localLinearVelocity.setter
    def localLinearVelocity(self, val: Vector):
        self.game_object.localLinearVelocity = val

    @property
    def worldAngularVelocity(self) -> Vector:
        return self.game_object.worldAngularVelocity

    @worldAngularVelocity.setter
    def worldAngularVelocity(self, val: Vector):
        self.game_object.worldAngularVelocity = val

    @property
    def localAngularVelocity(self) -> Vector:
        return self.game_object.localAngularVelocity

    @localAngularVelocity.setter
    def localAngularVelocity(self, val: Vector):
        self.game_object.localAngularVelocity = val

    @property
    def worldTransform(self) -> Matrix:
        return self.game_object.worldTransform

    @worldTransform.setter
    def worldTransform(self, val: Matrix):
        self.game_object.worldTransform = val


def get_curve_length(curve: KX_GameObject):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return sum(s.calc_length() for s in curve.blenderObject.evaluated_get(depsgraph).data.splines)


class ULCurve(GameObject):
    """Wrapper class for creating and handling curves more easily.

    :param `name`: Name of this curve object.
    :param `bevel_depth`: Define the "thickness" of the curve. This will add
    geometry along the spline.
    :param `dimensions`: Set the coordinate space in which to calculate the
    curve.
    :param `material`: The material to use for bevel geometry.
    :param `collection`: The collection to which to add the curve. Leave at
    `None` to use scene collection.
    """

    _deprecated = True

    def __init__(
        self,
        name: str,
        bevel_depth: float = 0.0,
        dimensions: int = 3,
        material: str or Material =None,
        collection: str = None
    ) -> None:
        if self._deprecated:
            print('[UPLOGIC] ULCurve class will be renamed to "Curve" in future releases!')
        self.game_object = create_curve(
            name,
            bevel_depth,
            dimensions,
            material,
            collection
        )

    @property
    def name(self):
        """Name of the game object (Read-Only)."""
        return self.game_object.name

    @name.setter
    def name(self, val):
        print('Curve.name is read-only!')

    @property
    def points(self):
        """Points of the curve. These points use global coordinates."""
        splines = self.game_object.blenderObject.data.splines
        return splines[0].points if len(splines) > 0 else []

    @points.setter
    def points(self, val):
        if val != self.points:
            set_curve_points(self.game_object, val)

    @property
    def bevel_depth(self):
        """Thickness of the curve geometry."""
        return self.game_object.blenderObject.data.bevel_depth

    @bevel_depth.setter
    def bevel_depth(self, val):
        self.game_object.blenderObject.data.bevel_depth = val

    @property
    def length(self):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        return sum(s.calc_length() for s in self.blenderObject.evaluated_get(depsgraph).data.splines)

    @length.setter
    def length(self, val):
        print('Curve.length is read-only!')

    @property
    def path_duration(self):
        return self.blenderObject.data.path_duration

    @path_duration.setter
    def path_duration(self, val):
        self.game_object.blenderObject.data.path_duration = val


class Curve(ULCurve):
    _deprecated = False

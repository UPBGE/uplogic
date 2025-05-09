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


def xrot_to(
    rotating_object,
    target_pos,
    front_axis_code=1,
    factor=1
):
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
    """Rotate an object around a local axis towards a point
    
    :param `object`:
    :param `target`:
    :param `rotation_axis`:
    :param `front_axis`:
    :param `factor`:
    """
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


def move_to(game_object: KX_GameObject, target: Vector, speed: float):
    direction = (game_object.worldPosition - target)
    if direction.length < speed:
        game_object.worldPosition = target
        return True
    direction.normalize()
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
    points: list,
    loop: bool = False,
    type: str = 'POLY'
) -> None:
    """Set the curve points of a `KX_GameObject` containing a `bpy.types.Curve` object.

    :param `curve`: `KX_GameObject`
    :param `points`: A list of points to use for the curve.
    """
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

    def __init__(self, game_object: KX_GameObject) -> None:
        self.game_object: KX_GameObject = game_object
        self.data = self.game_object.blenderObject.data

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
    def children(self):
        return self.game_object.children

    @property
    def children_recursive(self):
        return self.game_object.childrenRecursive

    @property
    def mass(self):
        return getattr(self.game_object, 'mass', 0)

    @mass.setter
    def mass(self, val):
        self.game_object.mass = val

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
    
    def move_to(self, target, speed):
        return move_to(self, target, speed)


def get_curve_length(curve: KX_GameObject):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return sum(s.calc_length() for s in curve.blenderObject.evaluated_get(depsgraph).data.splines)


def evaluate_curve(curve: KX_GameObject, factor: float = .5):
    eval_obj = bpy.data.objects.new(f'{curve.name}_eval_obj', object_data=None)
    bpy.context.collection.objects.link(eval_obj)
    bobj = curve.blenderObject
    const = eval_obj.constraints.new('FOLLOW_PATH')
    const.target = bobj
    time = bobj.data.eval_time
    bobj.data.eval_time = bobj.data.path_duration * factor
    bpy.context.view_layer.update()
    matrix = eval_obj.matrix_local
    bpy.data.objects.remove(eval_obj)
    bobj.data.eval_time = time
    return Vector((matrix[0][3], matrix[1][3], matrix[2][3]))


class Curve(GameObject):
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
            print('[UPLOGIC] ULCurve class will be renamed to "Curve" in future releases!')
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
        eval_obj = bpy.data.objects.get(f'{self.name}_eval_obj', None)
        if eval_obj is None:
            eval_obj = bpy.data.objects.new(f'{self.name}_eval_obj', object_data=None)
            bpy.context.collection.objects.link(eval_obj)
            const = eval_obj.constraints.new('FOLLOW_PATH')
            const.target = self.blenderObject
        return eval_obj

    def _create_dots(self):
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
        if self._array_object is not None:
            bpy.data.objects.remove(self._array_object)
        self._array_object = None
        self.data.bevel_depth = self.bevel_depth

    def _make_array(self):
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
        if self.style == "dots":
            self._create_dots()
        if self.style == "dashes":
            self._create_dashes()
        if self.style == 'line':
            # XXX: Investigate bevel_depth set to 0 if setting style attributes after setting radius
            self._remove_style()

    @property
    def style_spacing(self):
        return self._style_spacing

    @style_spacing.setter
    def style_spacing(self, val):
        self._style_spacing = val
        self._restyle()

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, val):
        if val == self.style:
            return
        self._style = val
        self._restyle()

    @property
    def dash_length(self):
        return self._dash_length

    @dash_length.setter
    def dash_length(self, val):
        self._dash_length = val
        self._restyle()

    @property
    def material(self):
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
        """Name of the game object (Read-Only)."""
        return self.game_object.name

    @name.setter
    def name(self, val: str):
        print('Curve.name is Read-Only!')

    @property
    def loop(self):
        """Name of the game object (Read-Only)."""
        return self._loop

    @loop.setter
    def loop(self, val: bool):
        self._loop = val
        self.points = self.points

    @property
    def points(self):
        """Points of the curve in global space."""
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
        """Thickness of the curve geometry as diameter."""
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
        '''Length of the curve (read-only).'''
        depsgraph = bpy.context.evaluated_depsgraph_get()
        return sum(s.calc_length() for s in self.blenderObject.evaluated_get(depsgraph).data.splines)

    @length.setter
    def length(self, val):
        print('Curve.length is read-only!')

    @property
    def path_duration(self):
        '''The number of frames that are needed to traverse the path, defining the maximum value for the "Evaluation Time" setting.'''
        return self.blenderObject.data.path_duration

    @path_duration.setter
    def path_duration(self, val):
        self.data.path_duration = val

    @property
    def resolution(self):
        return self.data.resolution_u

    @resolution.setter
    def resolution(self, val):
        self.data.resolution_u = int(val)

    @property
    def time(self):
        return self.data.eval_time

    @time.setter
    def time(self, val):
        self.data.eval_time = val

    def evaluate(self, factor):
        '''Get the world space coordinates on the curve at a given progress.'''
        time = self.blenderObject.data.eval_time
        eval_obj = self.eval_obj
        self.blenderObject.data.eval_time = self.path_duration * factor
        bpy.context.view_layer.update()
        matrix = eval_obj.matrix_local
        if not self.use_evaluate:
            bpy.data.objects.remove(eval_obj)
        self.blenderObject.data.eval_time = time
        return Vector((matrix[0][3], matrix[1][3], matrix[2][3]))
        # return Vector()


class ULCurve(Curve):
    _deprecated = True


class Mesh():

    def __init__(self, mesh: bpy.types.Mesh):
        self.blenderMesh: bpy.types.Mesh = mesh

    def applyRotation(self, rotation, local=False):
        rot = Euler(rotation)
        self.blenderMesh.transform(
            rot.to_matrix().to_4x4()
        )


def add_object(name: str | KX_GameObject, ref: str | KX_GameObject = None, time = 0, dupli = False):
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

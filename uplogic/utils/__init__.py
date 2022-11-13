'''TODO: Documentation
'''
from .lights import ULLight  # noqa
from .lights import make_unique_light  # noqa
from .nodetrees import get_geom_socket  # noqa
from .nodetrees import get_group_socket  # noqa
from .nodetrees import get_material_socket  # noqa
from .nodetrees import get_world_socket  # noqa
from .nodetrees import modify_geom_socket  # noqa
from .nodetrees import modify_material_socket  # noqa
from .nodetrees import modify_world_socket  # noqa
from .nodetrees import set_geom_socket  # noqa
from .nodetrees import set_group_socket  # noqa
from .nodetrees import set_material_socket  # noqa
from .nodetrees import set_world_socket  # noqa
from .objects import ULCurve  # noqa
from .objects import controller_brick_status  # noqa
from .objects import controller_brick  # noqa
from .objects import create_curve  # noqa
from .objects import set_curve_points  # noqa
from .raycasting import raycast  # noqa
from .raycasting import raycast_camera  # noqa
from .raycasting import raycast_face  # noqa
from .raycasting import raycast_projectile  # noqa
from .raycasting import raycast_mouse  # noqa
from .scene import set_scene  # noqa
from .visuals import draw_box  # noqa
from .visuals import draw_cube  # noqa
from .visuals import draw_line  # noqa
from .visuals import draw_points  # noqa
from .scene import FileLoader  # noqa
from .scene import SceneLoader  # noqa
from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Matrix
from mathutils import Vector
import time as t

import bpy
import json
import math
import operator


###############################################################################
# CONSTANTS
###############################################################################

class _Status(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name


NO_VALUE = _Status("NO_VALUE")
STATUS_WAITING = _Status("WAITING")
STATUS_READY = _Status("READY")
STATUS_INVALID = _Status("INVALID")


# uplogic game properties
VEHICLE = '.ulvehicleconst'
SHIP = '.ulshipconst'
FLOATSAM = '.ulfloatsamconst'
WATER = '.ulwater'

STREAMTYPE_DOWNSTREAM = 0
STREAMTYPE_UPSTREAM = 1

DISCONNECT_MSG = '!DISCONNECT'


LOGIC_OPERATORS = [
    operator.eq,
    operator.ne,
    operator.gt,
    operator.lt,
    operator.ge,
    operator.le
]


OPERATORS = {
    "ADD": operator.add,
    "DIV": operator.truediv,
    "MUL": operator.mul,
    "SUB": operator.sub,
    'FDIV': operator.floordiv,
    'MATMUL': operator.matmul,
    'MOD': operator.mod,
    'POW': operator.pow
}


LO_AXIS_TO_STRING_CODE = {
    0: "X", 1: "Y", 2: "Z",
    3: "-X", 4: "-Y", 5: "-Z",
}


LO_AXIS_TO_VECTOR = {
    0: Vector((1, 0, 0)), 1: Vector((0, 1, 0)),
    2: Vector((0, 0, 1)), 3: Vector((-1, 0, 0)),
    4: Vector((0, -1, 0)), 5: Vector((0, 0, -1)),
}


###############################################################################
# LOGIC NODES
###############################################################################


def _name_query(named_items, query):
    assert len(query) > 0
    postfix = (query[0] == "*")
    prefix = (query[-1] == "*")
    infix = (prefix and postfix)
    if infix:
        token = query[1:-1]
        for item in named_items:
            if token in item.name:
                return item
    if prefix:
        token = query[:-1]
        for item in named_items:
            if item.name.startswith(token):
                return item
    if postfix:
        token = query[1:]
        for item in named_items:
            if item.name.endswith(token):
                return item
    for item in named_items:
        if item.name == query:
            return item
    return None


def check_game_object(query, scene=None):
    '''TODO: Documentation
    '''
    if not scene:
        scene = logic.getCurrentScene()
    else:
        scene = scene
    if (query is None) or (query == ""):
        return
    if not is_invalid(scene):
        # find from scene
        return _name_query(scene.objects, query)


def compute_distance(parama, paramb) -> float:
    '''TODO: Documentation
    '''
    if is_invalid(parama):
        return None
    if is_invalid(paramb):
        return None
    if hasattr(parama, "getDistanceTo"):
        return parama.getDistanceTo(paramb)
    if hasattr(paramb, "getDistanceTo"):
        return paramb.getDistanceTo(parama)
    va = Vector(parama)
    vb = Vector(paramb)
    return (va - vb).length


def debug(message: str):
    if not hasattr(bpy.types.Scene, 'logic_node_settings'):
        return
    if not bpy.context or not bpy.context.scene:
        return
    if not bpy.context.scene.logic_node_settings.use_node_debug:
        return
    else:
        print('[UPLOGIC] ' + message)


def is_invalid(*a) -> bool:
    for ref in a:
        if ref is None or ref is STATUS_WAITING or ref == '':
            return True
        if not hasattr(ref, "invalid"):
            continue
        elif ref.invalid:
            return True
    return False


def is_waiting(*args) -> bool:
    if STATUS_WAITING in args:
        return True
    return False


def make_valid_name(name):
    valid_characters = (
        "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    clsname = name.replace(' ', '_')
    stripped_name = "".join(
        [c for c in clsname if c in valid_characters]
    )
    return stripped_name


def not_met(*conditions) -> bool:
    for c in conditions:
        if (
            c is STATUS_WAITING or
            c is None or
            c is False
        ):
            return True
    return False


def load_user_module(module_name):
    import sys
    exec(f"import {module_name}")
    return sys.modules[module_name]


def unload_nodes(a, b):
    if not hasattr(bpy.types.Scene, 'nl_globals_initialized'):
        return
    delattr(bpy.types.Scene, 'nl_globals_initialized')


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


def project_vector3(v, xi, yi):
    return Vector((v[xi], v[yi]))


def xrot_to(
    rotating_object,
    target_pos,
    front_axis_code=0,
    factor=1
):
    front_vector = LO_AXIS_TO_VECTOR[front_axis_code]
    vec = rotating_object.getVectTo(target_pos)[1]
    vec = project_vector3(vec, 1, 2)
    vec.normalize()
    front_vector = rotating_object.getAxisVect(front_vector)
    front_vector = project_vector3(front_vector, 1, 2)
    signed_angle = vec.angle_signed(front_vector, None)
    if signed_angle is None:
        return
    abs_angle = abs(signed_angle)
    if abs_angle < 0.01:
        return True
    angle_sign = (signed_angle > 0) - (signed_angle < 0)
    drot = angle_sign * abs_angle * clamp(factor)
    eulers = rotating_object.localOrientation.to_euler()
    eulers[0] += drot
    rotating_object.localOrientation = eulers
    return False


def yrot_to(
    rotating_object,
    target_pos,
    front_axis_code=0,
    factor=1
):
    front_vector = LO_AXIS_TO_VECTOR[front_axis_code]
    vec = rotating_object.getVectTo(target_pos)[1]
    vec = project_vector3(vec, 2, 0)
    vec.normalize()
    front_vector = rotating_object.getAxisVect(front_vector)
    front_vector = project_vector3(front_vector, 2, 0)
    signed_angle = vec.angle_signed(front_vector, None)
    if signed_angle is None:
        return
    abs_angle = abs(signed_angle)
    if abs_angle < 0.01:
        return True
    angle_sign = (signed_angle > 0) - (signed_angle < 0)
    drot = angle_sign * abs_angle * clamp(factor)
    eulers = rotating_object.localOrientation.to_euler()
    eulers[1] += drot
    rotating_object.localOrientation = eulers
    return False


def zrot_to(
    rotating_object,
    target_pos,
    front_axis_code=0,
    factor=1
):
    front_vector = LO_AXIS_TO_VECTOR[front_axis_code]
    vec = rotating_object.getVectTo(target_pos)[1]
    vec = project_vector3(vec, 0, 1)
    vec.normalize()
    front_vector = rotating_object.getAxisVect(front_vector)
    front_vector = project_vector3(front_vector, 0, 1)
    signed_angle = vec.angle_signed(front_vector, None)
    if signed_angle is None:
        return True
    abs_angle = abs(signed_angle)
    if abs_angle < 0.01:
        return True
    angle_sign = (signed_angle > 0) - (signed_angle < 0)
    drot = angle_sign * abs_angle * clamp(factor)
    eulers = rotating_object.localOrientation.to_euler()
    eulers[2] += drot
    rotating_object.localOrientation = eulers
    return False


def rot_to(
    rot_axis_index,
    rotating_object,
    target_pos,
    front_axis_code,
    factor=1
):
    if rot_axis_index == 0:
        return xrot_to(
            rotating_object,
            target_pos,
            front_axis_code,
            factor
        )
    elif rot_axis_index == 1:
        return yrot_to(
            rotating_object,
            target_pos,
            front_axis_code,
            factor
        )
    elif rot_axis_index == 2:
        return zrot_to(
            rotating_object,
            target_pos,
            front_axis_code,
            factor
        )


###############################################################################
# SCENE
###############################################################################


def get_closest_instance(game_obj: GameObject, name: str):
    '''TODO: Documentation
    '''
    objs = []
    distances = {}
    for obj in logic.getCurrentScene().objects:
        if obj.name == name:
            objs.append(obj)
    for obj in objs:
        distances[game_obj.getDistanceTo(obj)] = obj
    return distances[min(distances.keys())]


def is_water(game_object: GameObject):
    return WATER in game_object.getPropertyNames()


def get_child_by_name(obj, child, recursive=True, partial=False):
    children = obj.childrenRecursive if recursive else obj.children
    if partial:
        for c in children:
            if child in c.name:
                return c
    else:
        return children.get(child)


def check_vr_session_status() -> tuple[Vector, Matrix]:
    """Get the current position and orientation of connected VR headset.
    :returns: `tuple` of (`Vector`, `Matrix`)
    """
    session = bpy.context.window_manager.xr_session_state
    return session is not None


###############################################################################
# MATH
###############################################################################


def clamp(value: float or Vector, min: float = 0, max: float = 1) -> float:
    """Clamp a value in between two other values.

    :param value: input value
    :param min: minimum value
    :param max: maximum value

    :returns: clamped value as float
    """
    if isinstance(value, Vector):
        return vec_clamp(value, min, max)
    if value < min:
        return min
    if value > max:
        return max
    return value


def cycle(value: float or Vector, min: float = 0, max: float = 1) -> float:
    """Clamp a value in between two other values.

    :param value: input value
    :param min: minimum value
    :param max: maximum value

    :returns: clamped value as float
    """
    if isinstance(value, Vector):
        return vec_clamp(value, min, max)
    if value < min:
        return max
    if value > max:
        return min
    return value


def vec_clamp(vec: Vector, min: float = 0, max: float = 1) -> Vector:
    """Clamp length of a vector.

    :param value: `Vector`
    :param min: minimum length
    :param max: maximum length

    :returns: clamped vector as float
    """
    vec = vec.copy()
    if vec.length < min:
        vec.normalize()
        return vec * min
    if vec.length > max:
        vec.normalize()
        return vec * max
    return vec


def interpolate(a: float, b: float, fac: float, threshold: float = 0.001) -> float:
    """Interpolate between 2 values using a factor.

    :param a: starting value
    :param b: target value
    :param fac: interpolation factor

    :returns: calculated value as float
    """
    if -threshold < a-b < threshold:
        return b
    return (fac * b) + ((1-fac) * a)


def lerp(a: float, b: float, fac: float) -> float:
    """Interpolate between 2 values using a factor.

    :param a: starting value
    :param b: target value
    :param fac: interpolation factor

    :returns: calculated value as float
    """
    if -.001 < a-b < .001:
        return b
    return (fac * b) + ((1-fac) * a)


def vec_abs(vec):
    """Make every value of this vector positive.\n
    Only supports less than 4 Dimensions.

    :param `a`: `Vector`

    :returns: positive vector
    """
    vec = vec.copy()
    vec.x = abs(vec.x)
    vec.y = abs(vec.y)
    vec.z = abs(vec.z)
    return vec


def get_angle(a: Vector, b: Vector, up=Vector((0, 0, 1))) -> float:
    """Get the angle between the direction from a to b and up.

    :param `a`: `Vector` a
    :param `b`: `Vector` b
    :param `up`: compare direction

    :returns: calculated value as float
    """
    direction = get_direction(Vector(a), Vector(b))
    rad: float = direction.angle(up)
    deg: float = rad * 180/math.pi
    return deg


def get_raw_angle(a: Vector, b: Vector) -> float:
    """Get the angle between the direction from a to b and up.

    :param `a`: `Vector` a
    :param `b`: `Vector` b
    :param `up`: compare direction

    :returns: calculated value as float
    """
    rad: float = a.angle(b)
    deg: float = rad * 180/math.pi
    return deg


def get_direction(a, b, local=False) -> Vector:
    """Get the direction from one vector to another.

    :param `a`: `Vector` a
    :param `b`: `Vector` b
    :param `local`: use local space (position only)

    :returns: direction as `Vector`
    """
    start = a.worldPosition.copy() if hasattr(a, "worldPosition") else a
    if hasattr(b, "worldPosition"):
        b = b.worldPosition.copy()
    if local:
        b = start + b
    d = b - start
    d.normalize()
    return d


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float, clamp=(None, None)) -> float:
    """Map a value from one range to another.
    
    :param `value`: Value to be remapped.
    :param `in_min`: Lower end of the original range.
    :param `in_max`: Upper end of the original range.
    :param `out_min`: Lower end of the new range.
    :param `out_max`: Upper end of the new range.
    :param `clamp`: Clamp the modified value.
    """
    result = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if clamp[0] is not None and result < clamp[0]:
        return clamp[0]
    if clamp[1] is not None and result > clamp[1]:
        return clamp[1]
    return result


def screen_to_world(x:float = None, y: float = None, distance: float = 10) -> Vector:
    """Get the world coordinates of a point on the screen in a given distance.
    
    :param `x`: X position on the screen. Leave at `None` to use mouse position.
    :param `y`: Y position on the screen. Leave at `None` to use mouse position.
    :param `distance`: The distance from the camera at which to get the position.
    
    :returns: Position as `Vector`
    """

    camera = logic.getCurrentScene().active_camera
    mouse = logic.mouse
    x = x if x else mouse.position[0]
    y = y if y else mouse.position[1]
    direction = camera.getScreenVect(x, y)
    origin = camera.worldPosition
    aim = direction * -distance
    return origin + (aim)


def mouse_over(game_object: GameObject) -> bool:
    scene = game_object.scene
    camera = scene.active_camera
    distance = 2.0 * camera.getDistanceTo(game_object)
    mouse = logic.mouse
    mouse_position = mouse.position
    target = camera.getScreenRay(
        mouse_position[0],
        mouse_position[1],
        distance
    )
    return target is game_object


def get_local(obj, target) -> Matrix:
    return obj.worldTransform.inverted() @ target


def get_collision_bitmask(
    slot_0: float = 1,
    slot_1: float = 1,
    slot_2: float = 1,
    slot_3: float = 1,
    slot_4: float = 1,
    slot_5: float = 1,
    slot_6: float = 1,
    slot_7: float = 1,
    slot_8: float = 1,
    slot_9: float = 1,
    slot_10: float = 1,
    slot_11: float = 1,
    slot_12: float = 1,
    slot_13: float = 1,
    slot_14: float = 1,
    slot_15: float = 1
) -> int:
    slots = [slot_0, slot_1, slot_2, slot_3, slot_4, slot_5, slot_6, slot_7, slot_8, slot_9, slot_10, slot_11, slot_12, slot_13, slot_14, slot_15]
    return sum([slots[idx] * (2**idx) for idx in range(16)])

from mathutils import Vector
from bge import logic
from bge.types import KX_GameObject as GameObject
import math


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
    if isinstance(a, Vector) or isinstance(b, Vector):
        print('[UPLOGIC] Warning: utils.interpolate() will not work for Vector anymore; Use mathutils.Vector.lerp(vec2, fac) instead!')
    if -threshold < a-b < threshold:
        return b
    return (fac * b) + ((1-fac) * a)


def lerp(a: float, b: float, fac: float, threshold: float = 0.001) -> float:
    """Interpolate between 2 values using a factor.

    :param a: starting value
    :param b: target value
    :param fac: interpolation factor

    :returns: calculated value as float
    """
    if isinstance(a, Vector) or isinstance(b, Vector):
        print('[UPLOGIC] Warning: utils.lerp() will not work for Vector anymore; Use mathutils.Vector.lerp(vec2, fac) instead!')
    if -threshold < a-b < threshold:
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


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float, clamp: bool = False) -> float:
    """Map a value from one range to another.
    
    :param `value`: Value to be remapped.
    :param `in_min`: Lower end of the original range.
    :param `in_max`: Upper end of the original range.
    :param `out_min`: Lower end of the new range.
    :param `out_max`: Upper end of the new range.
    :param `clamp`: Clamp the modified value.
    """
    result = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if clamp and result < out_min:
        return out_min
    if clamp and result > out_max:
        return out_max
    return result


def map_range_vector(value: float, in_min: float, in_max: float, out_min: float, out_max: float, clamp: bool = False) -> float:
    """Map a vector from one range to another.

    :param `value`: Value to be remapped.
    :param `in_min`: Lower end of the original range.
    :param `in_max`: Upper end of the original range.
    :param `out_min`: Lower end of the new range.
    :param `out_max`: Upper end of the new range.
    :param `clamp`: Clamp the modified value.
    """
    outvec = Vector(value)
    for i in range(len(value)):
        result = (value[i] - in_min[i]) * (out_max[i] - out_min[i]) / (in_max[i] - in_min[i]) + out_min[i]
        if clamp and result < out_min[i]:
            result = out_min[i]
        if clamp and result > out_max[i]:
            result = out_max[i]
        outvec[i] = result
    return outvec


def world_to_screen(position: Vector = Vector((0, 0, 0)), inv_y: bool = True) -> Vector:
    pos = Vector(logic.getCurrentScene().active_camera.getScreenPosition(position))
    if inv_y:
        pos[1] = 1 - pos[1]
    return pos


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


def get_local(obj, target) -> Vector:
    return obj.worldTransform.inverted() @ target


def get_bitmask(
    *slots: int, all=False
) -> int:
    """Get the collision bitmask value for the provided slot indices. Slots range from 0 to 15.
    
    :param `slots`: Arbitrary arguments, slots from 0-15 as int.
    :param `all`: Get the bitmask value of all slots combined, ignores `slots` argument."""
    if not all and not slots:
        return 0
    mask = 0
    for slot in range(16) if all else slots:
        mask += 1 << slot
    return mask

def get_collision_bitmask(
    *slots: int, all=False
) -> int:
    return get_bitmask(*slots, all)


def project_vector3(v, xi, yi):
    return Vector((v[xi], v[yi]))


def rotate2d(origin, pivot, angle):
    angle = math.radians(angle)
    return Vector((
        ((origin[0] - pivot[0]) * math.cos(angle)) - ((origin[1] - pivot[1]) * math.sin(angle)) + pivot[0],
        ((origin[0] - pivot[0]) * math.sin(angle)) + ((origin[1] - pivot[1]) * math.cos(angle)) + pivot[1]
    ))


def rotate3d(origin, pivot, angle, axis=2):
    angle = math.radians(angle)
    if axis == 0:
        return Vector((
            origin[0],
            ((origin[1] - pivot[1]) * math.cos(angle)) - ((origin[2] - pivot[2]) * math.sin(angle)) + pivot[1],
            ((origin[1] - pivot[1]) * math.sin(angle)) + ((origin[2] - pivot[2]) * math.cos(angle)) + pivot[2]
        ))
    elif axis == 1:
        return Vector((
            ((origin[0] - pivot[0]) * math.cos(angle)) - ((origin[2] - pivot[2]) * math.sin(angle)) + pivot[0],
            origin[1],
            ((origin[0] - pivot[0]) * math.sin(angle)) + ((origin[2] - pivot[2]) * math.cos(angle)) + pivot[2]
        ))
    elif axis == 2:
        return Vector((
            ((origin[0] - pivot[0]) * math.cos(angle)) - ((origin[1] - pivot[1]) * math.sin(angle)) + pivot[0],
            ((origin[0] - pivot[0]) * math.sin(angle)) + ((origin[1] - pivot[1]) * math.cos(angle)) + pivot[1],
            origin[2]
        ))
    return origin


def rotate_by_axis(origin: Vector, pivot: Vector, angle: float, axis: Vector):

    angle = math.radians(angle)

    origin = origin.copy() - pivot

    z_null = Vector((axis.x, axis.y))
    if z_null.length:
        thz = z_null.angle_signed(Vector((1, 0)))
    else:
        thz = 90

    axis = Vector((
            (axis[0] * math.cos(-thz)) - (axis[1] * math.sin(-thz)),
            (axis[0] * math.sin(-thz)) + (axis[1] * math.cos(-thz)),
            axis[2]
    ))
    target_point = Vector((
            (origin[0] * math.cos(-thz)) - (origin[1] * math.sin(-thz)),
            (origin[0] * math.sin(-thz)) + (origin[1] * math.cos(-thz)),
            origin[2]
    ))

    thy = axis.angle(Vector((0, 0, 1)))

    target_point = Vector((
            (target_point[0] * math.cos(thy)) - (target_point[2] * math.sin(thy)),
            target_point[1],
            (target_point[0] * math.sin(thy)) + (target_point[2] * math.cos(thy))
    ))

    target_point = Vector((
            (target_point[0] * math.cos(angle)) - (target_point[1] * math.sin(angle)),
            (target_point[0] * math.sin(angle)) + (target_point[1] * math.cos(angle)),
            target_point[2]
    ))

    target_point = Vector((
            (target_point[0] * math.cos(-thy)) - (target_point[2] * math.sin(-thy)),
            target_point[1],
            (target_point[0] * math.sin(-thy)) + (target_point[2] * math.cos(-thy))
    ))

    target_point = Vector((
            (target_point[0] * math.cos(thz)) - (target_point[1] * math.sin(thz)),
            (target_point[0] * math.sin(thz)) + (target_point[1] * math.cos(thz)),
            target_point[2]
    ))

    return pivot + target_point

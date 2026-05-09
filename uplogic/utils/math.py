'''Mathematical helper functions for uplogic, covering scalar math, vector operations,
range mapping, rotation utilities, and collision bitmask generation.
'''
from mathutils import Vector
from mathutils import Euler
from mathutils import Matrix
from bge import logic
from bge.types import KX_GameObject as GameObject
import math
from typing import overload


def matmul(a, b):
    '''Matrix-multiply *a* and *b* via the ``@`` operator.

    :param a: left-hand operand (matrix or vector)
    :param b: right-hand operand (matrix or vector)

    :returns: result of ``a @ b``
    '''
    return a @ b


def multadd(a, b, c):
    '''Returns ``a * b + c`` (multiply-add).

    :param a: multiplicand
    :param b: multiplier
    :param c: addend

    :returns: ``a * b + c``
    '''
    return a * b + c


def isqrt(a):
    '''Integer square root as ``a ** 0.5``.

    :param a: input value

    :returns: square root of *a*
    '''
    return a ** 1/2


def smin(a, b, c):
    '''Smooth minimum of *a* and *b* with smoothing radius *c*.

    Reduces to ``min(a, b)`` when *c* is 0.

    :param a: first value
    :param b: second value
    :param c: smoothing radius; ``0`` disables smoothing

    :returns: smooth minimum as float
    '''
    if (c != 0):
        h = max(c - abs(a - b), 0) / c
        return min(a, b) - h * h * h * c * (.166666666666666)
    else:
        return min(a, b)


def smax(a, b, c):
    '''Smooth maximum of *a* and *b* with smoothing radius *c*.

    Computed as the negated ``smin`` of the negated inputs.

    :param a: first value
    :param b: second value
    :param c: smoothing radius; ``0`` disables smoothing

    :returns: smooth maximum as float
    '''
    return -smin(-a, -b, c)


def sign(a):
    '''Returns ``1.0``, ``-1.0``, or ``0`` depending on the sign of *a*.

    :param a: input value

    :returns: ``1.0`` if *a* > 0, ``-1.0`` if *a* < 0, ``0`` if *a* == 0
    '''
    return (
        a if a == 0 else (
            1.0 if a > 0 else -1.0
        )
    )


def compare(a, b, c):
    '''Returns ``True`` when ``|a - b| <= c``.

    :param a: first value
    :param b: second value
    :param c: tolerance threshold

    :returns: ``True`` if the values are within *c* of each other
    '''
    return abs(a-b) <= c


def fraction(a):
    '''Fractional part of *a*, computed as ``a - floor(a)``.

    :param a: input value

    :returns: fractional part as float
    '''
    return a - math.floor(a)


def trunc_mod(a, b):
    '''Truncated modulo: ``trunc(a % b)``.

    :param a: dividend
    :param b: divisor

    :returns: truncated remainder as int
    '''
    return math.trunc(a % b)


def floor_mod(a, b):
    '''Floor modulo: ``floor(a % b)``.

    :param a: dividend
    :param b: divisor

    :returns: floored remainder as int
    '''
    return math.floor(a % b)


def wrap(value, max, min):
    '''Wraps *value* cyclically into the half-open interval ``[min, max)``.

    Returns *min* when the range is zero.

    :param value: value to wrap
    :param max: upper bound (exclusive)
    :param min: lower bound (inclusive)

    :returns: wrapped value
    '''
    _range = max - min
    return value - (_range * math.floor((value - min) / _range)) if _range != 0 else min


def snap(value, step):
    '''Snaps *value* to the nearest multiple of *step*.

    Returns ``0`` when *step* is 0.

    :param value: value to snap
    :param step: grid step size; passing ``0`` returns ``0``

    :returns: snapped value as float
    '''
    if (step == 0):
        return  0.0
    else:
        return math.floor(value / step) * step


def ping_pong(value, scale):
    '''Bounces *value* back and forth within ``[0, scale]``.

    :param value: input value
    :param scale: upper bound of the bounce range

    :returns: ping-ponged value as float
    '''
    if (scale == 0.0):
        return 0.0
    return abs(fraction((value - scale) / (scale * 2.0)) * scale * 2.0 - scale)


def _min(a, b):
    '''Wrapper for the built-in ``min``.

    :param a: first value
    :param b: second value

    :returns: the smaller of *a* and *b*
    '''
    return min(a, b)


def _max(a, b):
    '''Wrapper for the built-in ``max``.

    :param a: first value
    :param b: second value

    :returns: the larger of *a* and *b*
    '''
    return max(a, b)


def _round(value):
    '''Wrapper for the built-in ``round``.

    :param value: input value

    :returns: rounded value as int
    '''
    return round(value)


def _log(value, base):
    '''Wrapper for ``math.log(value, base)``.

    :param value: input value
    :param base: logarithm base

    :returns: logarithm as float
    '''
    return math.log(value, base)


def _acos(value):
    '''Safe arc-cosine that clamps *value* to ``[0, 1]`` before calling ``math.acos``.

    :param value: input value

    :returns: arc-cosine in radians as float
    '''
    return math.acos(clamp(value))


def _asin(value):
    '''Safe arc-sine that clamps *value* to ``[0, 1]`` before calling ``math.asin``.

    :param value: input value

    :returns: arc-sine in radians as float
    '''
    return math.asin(clamp(value))


def _atan(value):
    '''Safe arc-tangent that clamps *value* to ``[0, 1]`` before calling ``math.atan``.

    :param value: input value

    :returns: arc-tangent in radians as float
    '''
    return math.atan(clamp(value))


def _lerp(a, b, fac):
    '''Thin wrapper around :func:`lerp`.

    :param a: starting value
    :param b: target value
    :param fac: interpolation factor

    :returns: interpolated value
    '''
    return lerp(a, b, fac)


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    '''Clamp *value* to the range ``[lower, upper]``.

    When *value* is a ``Vector``, delegates to ``vec_clamp`` to clamp the
    vector's length while preserving its direction.

    :param value: input value or ``Vector``
    :param lower: minimum allowed value (default ``0.0``)
    :param upper: maximum allowed value (default ``1.0``)

    :returns: clamped scalar as float, or length-clamped ``Vector``
    '''
    if isinstance(value, Vector):
        return vec_clamp(value, min, max)
    return max(lower, min(value, upper))


def cycle(value: float, min: float = 0, max: float = 1) -> float:
    '''Wrap *value* cyclically back into ``[min, max)``.

    Unlike ``clamp``, the value wraps around rather than being held at the
    boundary — reaching *max* brings it back to *min*, and going below *min*
    wraps it from *max*.

    :param value: input value
    :param min: lower boundary (inclusive)
    :param max: upper boundary (exclusive)

    :returns: cycled value as float
    '''
    if isinstance(value, Vector):
        return vec_clamp(value, min, max)
    if value >= max:
        return value - max
    if value < min:
        return max - abs(value - min)
    return value


def vec_clamp(vec: Vector, min: float = 0, max: float = 1) -> Vector:
    '''Clamp the *length* of a ``Vector`` to the range ``[min, max]``.

    The vector is normalised and then scaled to the boundary length when its
    length falls outside the given range; direction is always preserved.

    :param vec: input ``Vector``
    :param min: minimum vector length
    :param max: maximum vector length

    :returns: length-clamped ``Vector``
    '''
    vec = vec.copy()
    if vec.length < min:
        vec.normalize()
        return vec * min
    if vec.length > max:
        vec.normalize()
        return vec * max
    return vec


def interpolate(a: float, b: float, fac: float, threshold: float = 0.001) -> float:
    '''Weighted interpolation between *a* and *b*.

    Snaps directly to *b* when ``|a - b| < threshold``; otherwise performs a
    linear blend weighted by *fac*.

    :param a: starting value
    :param b: target value
    :param fac: interpolation factor (``0.0`` = full *a*, ``1.0`` = full *b*)
    :param threshold: snap-to-target tolerance (default ``0.001``)

    :returns: interpolated value as float
    '''
    if -threshold < a-b < threshold:
        return b
    return (fac * b) + ((1-fac) * a)


def lerp(a: float, b: float, fac: float, threshold: float = 0.001) -> float:
    '''Weighted interpolation between *a* and *b*.

    Snaps directly to *b* when ``|a - b| < threshold``; otherwise performs a
    linear blend weighted by *fac*. Equivalent to ``interpolate``; both exist
    for API compatibility.

    :param a: starting value
    :param b: target value
    :param fac: interpolation factor (``0.0`` = full *a*, ``1.0`` = full *b*)
    :param threshold: snap-to-target tolerance (default ``0.001``)

    :returns: interpolated value as float
    '''
    if -threshold < a-b < threshold:
        return b
    return (fac * b) + ((1-fac) * a)


def vec_abs(vec):
    '''Set every component of a 3D ``Vector`` to its absolute value.

    Only supports vectors with fewer than 4 dimensions (i.e. 2D or 3D).

    :param vec: input ``Vector``

    :returns: ``Vector`` with all components set to their absolute values
    '''
    vec = vec.copy()
    vec.x = abs(vec.x)
    vec.y = abs(vec.y)
    vec.z = abs(vec.z)
    return vec


def get_angle(a: Vector, b: Vector, up=Vector((0, 0, 1))) -> float:
    '''Angle in degrees between the direction from *a* to *b* and the *up* vector.

    The direction vector ``a -> b`` is computed first, then its angle against
    *up* is returned in degrees.

    :param a: origin ``Vector``
    :param b: target ``Vector``
    :param up: reference direction (default world Z ``(0, 0, 1)``)

    :returns: angle in degrees as float
    '''
    direction = get_direction(Vector(a), Vector(b))
    rad: float = direction.angle(up)
    deg: float = rad * 180/math.pi
    return deg


def get_raw_angle(a: Vector, b: Vector) -> float:
    '''Angle in degrees between two vectors directly (no direction calculation).

    Unlike ``get_angle``, no intermediate direction is computed — the angle is
    measured directly between the two supplied vectors.

    :param a: first ``Vector``
    :param b: second ``Vector``

    :returns: angle in degrees as float
    '''
    rad: float = a.angle(b)
    deg: float = rad * 180/math.pi
    return deg


def angle_signed(a: Vector, b: Vector, up: Vector) -> float:
    '''Signed angle between vectors *a* and *b* around *up* using ``atan2``.

    :param a: source direction ``Vector``
    :param b: target direction ``Vector``
    :param up: axis around which the sign is determined

    :returns: signed angle in radians as float
    '''
    return math.atan2(a.cross(b).dot(up), a.dot(b))


def get_direction(a, b, local=False) -> Vector:
    '''Normalised direction ``Vector`` from *a* to *b*.

    When *local* is ``True``, *b* is treated as a local offset from *a* rather
    than an absolute world position.

    :param a: origin position or ``KX_GameObject``
    :param b: target position or ``KX_GameObject``
    :param local: interpret *b* as a local offset from *a* (default ``False``)

    :returns: normalised direction ``Vector``
    '''
    start = a.worldPosition.copy() if hasattr(a, "worldPosition") else a
    if hasattr(b, "worldPosition"):
        b = b.worldPosition.copy()
    if local:
        b = start + b
    d = b - start
    d.normalize()
    return d


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float, clamp: bool = False) -> float:
    '''Remap *value* from the input range ``[in_min, in_max]`` to the output
    range ``[out_min, out_max]``.

    Returns *out_max* when the input range has zero width to avoid division by
    zero.

    :param value: value to be remapped
    :param in_min: lower end of the input range
    :param in_max: upper end of the input range
    :param out_min: lower end of the output range
    :param out_max: upper end of the output range
    :param clamp: clamp the result to ``[out_min, out_max]`` (default ``False``)

    :returns: remapped value as float
    '''
    div = (in_max - in_min)
    if div == 0:
        return out_max
    result = (value - in_min) * (out_max - out_min) / div + out_min
    if out_min > out_max:
        out_min, out_max = out_max, out_min
    if clamp and result < out_min:
        return out_min
    if clamp and result > out_max:
        return out_max
    return result


def map_range_vector(value: float, in_min: float, in_max: float, out_min: float, out_max: float, clamp: bool = False) -> float:
    '''Per-component range remap for vectors.

    Applies ``map_range`` to each component independently, allowing per-axis
    range remapping of a vector.

    :param value: vector to be remapped (any sequence type)
    :param in_min: per-component lower end of the input range
    :param in_max: per-component upper end of the input range
    :param out_min: per-component lower end of the output range
    :param out_max: per-component upper end of the output range
    :param clamp: clamp each component to its output range (default ``False``)

    :returns: remapped ``Vector``
    '''
    outvec = Vector(value)
    for i in range(len(value)):
        result = (value[i] - in_min[i]) * (out_max[i] - out_min[i]) / (in_max[i] - in_min[i]) + out_min[i]
        if clamp and result < out_min[i]:
            result = out_min[i]
        if clamp and result > out_max[i]:
            result = out_max[i]
        outvec[i] = result
    return outvec


def get_local(obj: GameObject, target: Vector) -> Vector:
    '''Transform *target* from world space into *obj*'s local space via the
    inverse world transform.

    :param obj: reference ``KX_GameObject`` whose world transform is inverted
    :param target: world-space position ``Vector`` to transform

    :returns: *target* expressed in *obj*'s local space as a ``Vector``
    '''
    return obj.worldTransform.inverted() @ target


def get_bitmask(
    *slots: int, all=False
) -> int:
    '''Build a 16-bit collision bitmask from the given slot indices 0–15.

    When *all* is ``True``, all 16 bits are set and *slots* is ignored.

    :param slots: arbitrary number of slot indices (each between 0 and 15)
    :param all: set all 16 bits, ignoring *slots* (default ``False``)

    :returns: bitmask value as int
    '''
    if not all and not slots:
        return 0
    mask = 0
    for slot in range(16) if all else slots:
        mask += 1 << slot
    return mask


def get_collision_bitmask(
    *slots: int, all=False
) -> int:
    '''Alias for ``get_bitmask``; retained for backwards compatibility.

    .. deprecated::
        Use ``get_bitmask`` instead.

    :param slots: arbitrary number of slot indices (each between 0 and 15)
    :param all: set all 16 bits, ignoring *slots* (default ``False``)

    :returns: bitmask value as int
    '''
    return get_bitmask(*slots, all)


def project_vector3(v, xi, yi):
    '''Extract a 2D ``Vector`` from components *xi* and *yi* of *v*.

    :param v: source 3D vector or sequence
    :param xi: index of the component to use as the X axis
    :param yi: index of the component to use as the Y axis

    :returns: 2D ``Vector`` ``(v[xi], v[yi])``
    '''
    return Vector((v[xi], v[yi]))


def rotate2d(origin, pivot, angle):
    '''Rotate a 2D point *origin* around *pivot* by *angle* degrees.

    :param origin: point to rotate as a 2-element sequence or ``Vector``
    :param pivot: centre of rotation as a 2-element sequence or ``Vector``
    :param angle: rotation angle in degrees

    :returns: rotated point as a 2D ``Vector``
    '''
    angle = math.radians(angle)
    return Vector((
        ((origin[0] - pivot[0]) * math.cos(angle)) - ((origin[1] - pivot[1]) * math.sin(angle)) + pivot[0],
        ((origin[0] - pivot[0]) * math.sin(angle)) + ((origin[1] - pivot[1]) * math.cos(angle)) + pivot[1]
    ))


def rotate3d(origin, pivot, angle, axis=2):
    '''Rotate a 3D point around *pivot* by *angle* degrees on the given *axis*.

    *axis* selects the world axis: ``0`` = X, ``1`` = Y, ``2`` = Z (default).
    Returns *origin* unchanged when *axis* is out of range.

    :param origin: point to rotate as a 3-element sequence or ``Vector``
    :param pivot: centre of rotation as a 3-element sequence or ``Vector``
    :param angle: rotation angle in degrees
    :param axis: axis index — ``0`` = X, ``1`` = Y, ``2`` = Z (default ``2``)

    :returns: rotated point as a 3D ``Vector``, or *origin* unchanged if *axis*
              is out of range
    '''
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
    '''Rotate *origin* around an arbitrary *axis* passing through *pivot* by
    *angle* degrees.

    The rotation is performed via a series of alignment rotations that bring
    *axis* onto the Z axis, rotate, then invert the alignment.

    :param origin: point to rotate as a ``Vector``
    :param pivot: centre of rotation as a ``Vector``
    :param angle: rotation angle in degrees
    :param axis: arbitrary rotation axis as a ``Vector``

    :returns: rotated point as a 3D ``Vector``
    '''
    angle = math.radians(angle)

    pivot = Vector(pivot)
    axis = Vector(axis)
    origin = Vector(origin) - pivot

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


def rotate_by_euler(origin: Vector, pivot: Vector, angles: Euler):
    '''Rotate *origin* around *pivot* by the ``Euler`` *angles*.

    :param origin: point to rotate as a ``Vector``
    :param pivot: centre of rotation as a ``Vector``
    :param angles: rotation expressed as an ``Euler`` object

    :returns: rotated point as a 3D ``Vector``
    '''
    origin = origin.copy() - pivot
    angles = Euler(angles)

    transmat = angles.to_matrix()

    return pivot + origin @ transmat

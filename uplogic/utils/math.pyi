from mathutils import Vector

def interpolate(a: float, b: float, fac: float) -> float:
    """Interpolate between 2 values using a factor.

    :param `a`: starting value
    :param `b`: target value
    :param `fac`: interpolation factor

    :returns: calculated value as float
    """
    pass

def lerp(a: float, b: float, fac: float) -> float:
    """Interpolate between 2 values using a factor.

    :param `a`: starting value
    :param `b`: target value
    :param `fac`: interpolation factor

    :returns: calculated value as float
    """
    pass

def clamp(value: float, min: float, max: float) -> float:
    """Clamp a value in between two other values.

    :param value: input value
    :param min: minimum value
    :param max: maximum value

    :returns: clamped value as float
    """


def cycle(value: float, min: float = 0, max: float = 1) -> float:
    """Clamp a value in between two other values.

    :param value: input value
    :param min: minimum value
    :param max: maximum value

    :returns: clamped value as float
    """
    pass


def vec_clamp(vec: Vector, min: float = 0, max: float = 1) -> Vector:
    """Clamp length of a vector.

    :param value: `Vector`
    :param min: minimum length
    :param max: maximum length

    :returns: clamped vector as float
    """
    pass


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Map a value from one range to another.
    
    :param `value`: Value to be remapped.
    :param `in_min`: Lower end of the original range.
    :param `in_max`: Upper end of the original range.
    :param `out_min`: Lower end of the new range.
    :param `out_max`: Upper end of the new range.
    """
    pass
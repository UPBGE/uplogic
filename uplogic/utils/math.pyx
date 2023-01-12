
cpdef double interpolate(double a, double b, double fac):
    return (fac * b) + ((1-fac) * a)


cpdef double lerp(double a, double b, double fac):
    return (fac * b) + ((1-fac) * a)


cpdef double clamp(double value, double min=0, double max=1):
    if value < min:
        return min
    if value > max:
        return max
    return value


cpdef double cycle(double value, double min=0, double max=1):
    if value < min:
        return max
    if value > max:
        return min
    return value


def vec_clamp(vec, double min=0, double max=1):
    from mathutils import Vector
    vec = vec.copy()
    if vec.length < min:
        vec.normalize()
        return vec * min
    if vec.length > max:
        vec.normalize()
        return vec * max
    return vec


cpdef double map_range(double value, double in_min, double in_max, double out_min, double out_max):
    """Map a value from one range to another.
    
    :param `value`: Value to be remapped.
    :param `in_min`: Lower end of the original range.
    :param `in_max`: Upper end of the original range.
    :param `out_min`: Lower end of the new range.
    :param `out_max`: Upper end of the new range.
    """
    result = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return result
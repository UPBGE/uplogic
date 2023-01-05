from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_WAITING
from uplogic.utils import is_waiting
from uplogic.utils import is_invalid


class ULVectorMath(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.op = None
        self.vector = None
        self.vector_2 = None
        self.factor = None
        self.scale = None
        self.vector_3 = None
        self.ior = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        op = self.get_input(self.op)
        vector = self.get_input(self.vector)
        vector_2 = self.get_input(self.vector_2)
        vector_3 = self.get_input(self.vector_3)
        factor = self.get_input(self.factor)
        scale = self.get_input(self.scale)
        if is_waiting(
            op,
            factor
        ):
            return STATUS_WAITING
        if is_invalid(
            vector,
            vector_2
        ):
            return STATUS_WAITING
        calculations = {
            'scale': self.get_scale,
            'length': self.get_length,
            'distance': self.get_distance,
            'dot': self.get_dot,
            'faceforward': self.get_faceforward,
            'refract': self.get_refract,
            'reflect': self.get_reflect,
            'project': self.get_project,
            'cross': self.get_cross,
            'multadd': self.get_multadd,
            'divide': self.get_divide,
            'multiply': self.get_multiply,
            'subtract': self.get_subtract,
            'add': self.get_add,
            'normalize': self.get_normalize,
            'lerp': self.get_lerp,
            'negate': self.get_negate,
        }
        if vector:
            vector = vector.copy()
        if vector_2:
            vector_2 = vector_2.copy()
        if vector_3:
            vector_3 = vector_3.copy()
        return calculations[op](vector, vector_2, vector_3, factor, scale)

    def evaluate(self):
        self._set_ready()

    def get_scale(self, vec, vec2, vec3, fac, scale):
        return vec * scale

    def get_length(self, vec, vec2, vec3, fac, scale):
        return vec.length

    def get_distance(self, vec, vec2, vec3, fac, scale):
        return (vec - vec2).length

    def get_dot(self, vec, vec2, vec3, fac, scale):
        return vec.dot(vec2)

    def get_faceforward(self, vec, vec2, vec3, fac, scale):
        pass

    def get_refract(self, vec, vec2, vec3, fac, scale):
        pass

    def get_reflect(self, vec, vec2, vec3, fac, scale):
        return vec.reflect(vec2)

    def get_project(self, vec, vec2, vec3, fac, scale):
        return vec.project(vec2)

    def get_cross(self, vec, vec2, vec3, fac, scale):
        return vec.cross(vec2)

    def get_multadd(self, vec, vec2, vec3, fac, scale):
        return (vec * vec2) + vec3

    def get_divide(self, vec, vec2, vec3, fac, scale):
        return vec / vec2

    def get_multiply(self, vec, vec2, vec3, fac, scale):
        return vec * vec2

    def get_subtract(self, vec, vec2, vec3, fac, scale):
        return vec - vec2

    def get_add(self, vec, vec2, vec3, fac, scale):
        return vec + vec2

    def get_normalize(self, vec, vec2, vec3, fac, scale):
        return vec.normalized()

    def get_lerp(self, vec, vec2, vec3, fac, scale):
        return vec.lerp(vec2, fac)

    def get_negate(self, vec, vec2, vec3, fac, scale):
        vec.negate()
        return vec

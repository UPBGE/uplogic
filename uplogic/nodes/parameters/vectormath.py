from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector


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
        self.VOUT = ULOutSocket(self, self.get_done)
        self.calculations = {
            'scale': self.get_scale,
            'length': self.get_length,
            'distance': self.get_distance,
            'angle': self.get_angle,
            'angle_signed': self.get_angle_signed,
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
            'matmul': self.get_matmul,
            'normalize': self.get_normalize,
            'lerp': self.get_lerp,
            'slerp': self.get_slerp,
            'negate': self.get_negate,
        }

    def get_done(self):
        op = self.get_input(self.op)
        vector = self.get_input(self.vector)
        vector_2 = self.get_input(self.vector_2)
        vector_3 = self.get_input(self.vector_3)
        factor = self.get_input(self.factor)
        scale = self.get_input(self.scale)
        if vector:
            vector = vector.copy()
        if vector_2:
            vector_2 = vector_2.copy()
        if vector_3:
            vector_3 = vector_3.copy()
        return self.calculations[op](vector, vector_2, vector_3, factor, scale)

    def get_scale(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec * scale

    def get_length(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.length

    def get_distance(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return (vec - vec2).length

    def get_angle(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.angle(vec2)

    def get_angle_signed(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.angle_signed(vec2, vec3)

    def get_dot(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.dot(vec2)

    def get_faceforward(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec

    def get_refract(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec

    def get_reflect(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.reflect(vec2)

    def get_project(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.project(vec2)

    def get_cross(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.cross(vec2)

    def get_multadd(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return (vec * vec2) + vec3

    def get_divide(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec / fac

    def get_multiply(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec * vec2

    def get_matmul(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec @ vec2

    def get_subtract(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec - vec2

    def get_add(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec + vec2

    def get_normalize(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.normalized()

    def get_lerp(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.lerp(vec2, fac)

    def get_slerp(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        return vec.slerp(vec2, fac, vec3)

    def get_negate(self, vec: Vector, vec2: Vector, vec3: Vector, fac: float, scale: float):
        vec.negate()
        return vec

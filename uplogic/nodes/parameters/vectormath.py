from uplogic.nodes import ULParameterNode
from mathutils import Vector
from uplogic.utils.math import angle_signed
from uplogic.utils.math import wrap
from uplogic.utils.math import snap
import math


class VectorMathNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.operator = 0
        self.vector_a = None
        self.vector_b = None
        self.vector_c = None
        self.value = None
        self.RESULT = self.add_output(self.get_done)
        self.RESULT_VECTOR = self.add_output(self.get_done)
        
        self.calculations = [
            self.get_add,  # 0
            self.get_subtract,  # 1
            self.get_multiply,  # 2
            self.get_divide,  # 3
            self.get_multadd,  # 4
            self.get_matmul,  # 5
            self.get_angle,  # 6
            self.get_angle_signed,  # 7
            self.get_cross,  # 8
            self.get_project,  # 9
            self.get_reflect,  # 10
            self.get_refract,  # 11
            self.get_faceforward,  # 12
            self.get_dot,  # 13
            self.get_lerp,  # 14
            self.get_slerp,  # 15
            self.get_distance,  # 16
            self.get_length,  # 17
            self.get_scale,  # 18
            self.get_normalize,  # 19
            self.get_absolute,  # 20
            self.get_negate,  # 21
            self.get_min,  # 22
            self.get_max,  # 23
            self.get_round,  # 24
            self.get_floor,  # 25
            self.get_ceil,  # 26
            self.get_fraction,  # 27
            self.get_mod,  # 28
            self.get_wrap,  # 29
            self.get_snap,  # 30
            self.get_sine,  # 31
            self.get_cosine,  # 32
            self.get_tangent  # 33
        ]

    def get_done(self):
        vector_a = self.get_input(self.vector_a)
        vector_b = self.get_input(self.vector_b)
        vector_c = self.get_input(self.vector_c)
        value = self.get_input(self.value)
        if vector_a:
            vector_a = vector_a.copy()
        if vector_b:
            vector_b = vector_b.copy()
        if vector_c:
            vector_c = vector_c.copy()
        return self.calculations[self.operator](vector_a, vector_b, vector_c, value)

    def get_scale(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a * value

    def get_length(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.length

    def get_distance(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return (vector_a - vector_b).length

    def get_angle(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.angle(vector_b)

    def get_angle_signed(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return angle_signed(vector_a, vector_b, vector_c)

    def get_dot(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.dot(vector_b)

    def get_faceforward(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a if vector_c.dot(vector_b) < 0.0 else -vector_a

    def get_refract(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        k = 1.0 - value * value * (1.0 - vector_b.dot(vector_a) * vector_b.dot(vector_a))
        if (k < 0):
            return Vector((0, 0, 0))
        else:
            return value * vector_a - (value * vector_b.dot(vector_a) + math.sqrt(k)) * vector_b

    def get_reflect(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.reflect(vector_b)

    def get_project(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.project(vector_b)

    def get_cross(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.cross(vector_b)

    def get_multadd(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return (vector_a * vector_b) + vector_c

    def get_divide(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([e / vector_b[i] if vector_b[i] != 0 else 0 for i, e in enumerate(vector_a)])

    def get_multiply(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a * vector_b

    def get_matmul(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a @ vector_b

    def get_subtract(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a - vector_b

    def get_add(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a + vector_b

    def get_normalize(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.normalized()

    def get_lerp(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.lerp(vector_b, value)

    def get_slerp(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return vector_a.slerp(vector_b, value, vector_c)

    def get_negate(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        vector_a.negate()
        return vector_a

    def get_absolute(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([abs(e) for e in vector_a])

    def get_min(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([min(e) for e in vector_a])

    def get_max(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([max(e) for e in vector_a])

    def get_round(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([round(e) for e in vector_a])

    def get_floor(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([math.floor(e) for e in vector_a])

    def get_ceil(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([math.ceil(e) for e in vector_a])

    def get_fraction(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([e - math.floor(e) for e in vector_a])

    def get_mod(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([e % vector_b[i] if vector_b[i] != 0 else 0 for i, e in enumerate(vector_a)])

    def get_wrap(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([wrap(e, vector_b[i]) for i, e in enumerate(vector_a)])

    def get_snap(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([snap(e, vector_b[i]) for i, e in enumerate(vector_a)])

    def get_sine(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([e - math.sin(e) for e in vector_a])

    def get_cosine(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([e - math.cos(e) for e in vector_a])

    def get_tangent(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, value: float):
        return Vector([e - math.tan(e) for e in vector_a])

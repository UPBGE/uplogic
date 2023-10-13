from mathutils import Vector
from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULMath(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.operand_a = None
        self.operand_b = None
        self.operator = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        a = self.get_input(self.operand_a)
        b = self.get_input(self.operand_b)
        return self.operator(a, b)

    def get_vec_calc(self, vec, num):
        if len(vec) == 4:
            return Vector(
                (
                    self.operator(vec.x, num),
                    self.operator(vec.y, num),
                    self.operator(vec.z, num),
                    self.operator(vec.w, num)
                )
            )
        else:
            return Vector(
                (
                    self.operator(vec.x, num),
                    self.operator(vec.y, num),
                    self.operator(vec.z, num)
                )
            )

    def get_vec_vec_calc(self, vec, vec2):
        if len(vec) == 4 and len(vec2) == 4:
            return Vector(
                (
                    self.operator(vec.x, vec2.x),
                    self.operator(vec.y, vec2.y),
                    self.operator(vec.z, vec2.z),
                    self.operator(vec.w, vec2.w)
                )
            )
        else:
            return Vector(
                (
                    self.operator(vec.x, vec2.x),
                    self.operator(vec.y, vec2.y),
                    self.operator(vec.z, vec2.z)
                )
            )

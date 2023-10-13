from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector


class ULRangedThreshold(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.threshold = None
        self.min_value = None
        self.max_value = None
        self.operator = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        v = self.get_input(self.value)
        if self.min_value is not None:
            t = Vector((self.get_input(self.min_value), self.get_input(self.max_value)))
        else:
            t = self.get_input(self.threshold)
        value = self.calc_threshold(self.operator, v, t)
        return value

    def calc_threshold(self, op, v, t):
        if op == 'OUTSIDE':
            return v if (v < t.x or v > t.y) else 0
        if op == 'INSIDE':
            return v if (t.x < v < t.y) else 0

from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector


class ULWithinRange(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.range = None
        self.min_value = None
        self.max_value = None
        self.operator = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        v = self.get_input(self.value)
        if self.min_value is not None:
            r = Vector((self.get_input(self.min_value), self.get_input(self.max_value)))
        else:
            r = self.get_input(self.range)
        value = self.calc_range(self.operator, v, r)
        return value

    def calc_range(self, op, v, r):
        if op == 'OUTSIDE':
            return True if (v < r.x or v > r.y) else False
        if op == 'INSIDE':
            return True if (r.x < v < r.y) else False

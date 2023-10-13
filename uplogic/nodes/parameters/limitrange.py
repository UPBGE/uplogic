from mathutils import Vector
from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULLimitRange(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.threshold = Vector((0, 0))
        self.min_value = None
        self.max_value = None
        self.operator = None
        self.last_val = 0
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        v = self.get_input(self.value)
        t = self.get_input(self.threshold)
        if self.min_value is not None:
            t = Vector((self.get_input(self.min_value), self.get_input(self.max_value)))
        else:
            t = self.get_input(self.threshold)
        self.calc_threshold(self.operator, v, t)
        return self.last_val

    def calc_threshold(self, op, v, t):
        last = self.last_val
        if op == 'OUTSIDE':
            if (v < t.x or v > t.y):
                self.last_val = v
            else:
                self.last_val = t.x if last <= t.x else t.y
        if op == 'INSIDE':
            if (t.x < v < t.y):
                self.last_val = v
            else:
                self.last_val = t.x if v <= t.x else t.y

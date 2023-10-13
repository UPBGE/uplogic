from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULThreshold(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.else_z = None
        self.threshold = None
        self.operator = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        v = self.get_input(self.value)
        e = self.get_input(self.else_z)
        t = self.get_input(self.threshold)
        value = self.calc_threshold(self.operator, v, t, e)
        return value

    def calc_threshold(self, op, v, t, e):
        if op == 'GREATER':
            return v if v > t else (0 if e else t)
        if op == 'LESS':
            return v if v < t else (0 if e else t)

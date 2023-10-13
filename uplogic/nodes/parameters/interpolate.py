from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import lerp


class ULInterpolate(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.a = None
        self.b = None
        self.fac = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        a = self.get_input(self.a)
        b = self.get_input(self.b)
        fac = self.get_input(self.fac)
        return lerp(a, b, fac)

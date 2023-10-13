from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULColorRGBA(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.color = None
        self.output_vector = None
        self.OUTV = ULOutSocket(self, self.get_out_v)

    def get_out_v(self):
        c = self.get_input(self.color)
        c = c.copy()
        c.resize_4d()
        return c

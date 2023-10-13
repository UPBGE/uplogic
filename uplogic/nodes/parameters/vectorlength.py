from mathutils import Vector
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULVectorLength(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.input_v = None
        self.output_v = Vector()
        self.OUTV = ULOutSocket(self, self.get_out_v)

    def get_out_v(self):
        return self.get_input(self.input_v).length

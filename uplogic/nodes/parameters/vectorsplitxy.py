from mathutils import Vector
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULVectorSplitXY(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.input_v = None
        self.output_v = Vector((0, 0))
        self.OUTX = ULOutSocket(self, self.get_out_x)
        self.OUTY = ULOutSocket(self, self.get_out_y)

    def get_out_x(self):
        return self.output_v.x

    def get_out_y(self):
        return self.output_v.y

    def evaluate(self):
        vec = self.get_input(self.input_v)
        self.output_v = vec

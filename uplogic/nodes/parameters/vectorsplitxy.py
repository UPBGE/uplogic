from mathutils import Vector
from uplogic.nodes import ULParameterNode


class ULVectorSplitXY(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.input_v = Vector((0, 0))
        self.OUTX = self.add_output(self.get_out_x)
        self.OUTY = self.add_output(self.get_out_y)

    def get_out_x(self):
        return self.get_input(self.input_v).x

    def get_out_y(self):
        return self.get_input(self.input_v).y


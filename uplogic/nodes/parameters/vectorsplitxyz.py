from mathutils import Vector
from uplogic.nodes import ULParameterNode


class ULVectorSplitXYZ(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.input_v = Vector()
        self.OUTX = self.add_output(self.get_out_x)
        self.OUTY = self.add_output(self.get_out_y)
        self.OUTZ = self.add_output(self.get_out_z)

    def get_out_x(self):
        return self.get_input(self.input_v).x

    def get_out_y(self):
        return self.get_input(self.input_v).y

    def get_out_z(self):
        return self.get_input(self.input_v).z


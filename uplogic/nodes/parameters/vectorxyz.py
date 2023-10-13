from mathutils import Vector
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULVectorXYZ(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.input_x = None
        self.input_y = None
        self.input_z = None
        self.OUTV = ULOutSocket(self, self.get_out_v)

    def get_out_v(self):
        return Vector((
            self.get_input(self.input_x),
            self.get_input(self.input_y),
            self.get_input(self.input_z)
        ))


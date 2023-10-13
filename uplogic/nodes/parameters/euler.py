from mathutils import Euler
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULEuler(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.input_x = None
        self.input_y = None
        self.input_z = None
        self.order = 'XYZ'
        self.OUTV = ULOutSocket(self, self.get_out_v)

    def get_out_v(self):
        e = Euler(order=self.order)
        x = self.get_input(self.input_x)
        y = self.get_input(self.input_y)
        z = self.get_input(self.input_z)
        e.x = x
        e.y = y
        e.z = z
        return e

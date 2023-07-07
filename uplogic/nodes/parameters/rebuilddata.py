from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector, Matrix


class ULRebuildData(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.data = None
        self.read_as = 'builtin'
        self.dattypes = {
            'Vec2': Vector,
            'Vec3': Vector,
            'Vec4': Vector,
            'Mat3': Matrix,
            'Mat4': Matrix,
            'GameObj': Matrix
        }
        self.OUT = ULOutSocket(self, self.get_data)

    def get_data(self):
        dat = self.get_input(self.data)
        if self.read_as == 'builtin':
            return dat
        return self.dattypes[self.read_as](dat)

    def evaluate(self):
        self._set_ready()

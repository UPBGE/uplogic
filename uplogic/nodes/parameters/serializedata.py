from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.serialize import Vec2, Vec3, Vec4, Mat3, Mat4, GameObj


class ULSerializeData(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.data = None
        self.serialize_as = 'builtin'
        self.dattypes = {
            'Vec2': Vec2,
            'Vec3': Vec3,
            'Vec4': Vec4,
            'Mat3': Mat3,
            'Mat4': Mat4,
            'GameObj': GameObj,
        }
        self.OUT = ULOutSocket(self, self.get_data)

    def get_data(self):
        dat = self.get_input(self.data)
        if self.serialize_as == 'builtin':
            return dat
        return self.dattypes[self.serialize_as](dat)

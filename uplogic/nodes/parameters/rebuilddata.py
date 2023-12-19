from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector, Matrix
import bpy
from bge import logic


class ULRebuildData(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.data = None
        self.read_as = 'builtin'
        self.ret = None
        self.dattypes = {
            'Vec2': Vector,
            'Vec3': Vector,
            'Vec4': Vector,
            'Mat3': Matrix,
            'Mat4': Matrix
        }
        self.OUT = ULOutSocket(self, self.get_data)

    def get_data(self):
        return self.ret

    def evaluate(self):
        dat = self.get_input(self.data)
        if dat is None:
            return
        if self.read_as == 'builtin':
            self.ret = dat
            return
        if self.read_as == 'GameObj':
            bobj = bpy.data.objects.get(dat['data_id'])
            if bobj is None:
                self.ret = None
                return
            obj = logic.getCurrentScene().getGameObjectFromObject(bobj)
            for attr in dat:
                if attr == 'properties':
                    for prop in dat[attr]:
                        obj[prop] = dat[attr][prop]
                elif attr not in ['name', 'data_id']:
                    setattr(obj, attr, dat[attr])
            self.ret = obj
            return
        self.ret = self.dattypes[self.read_as](dat)

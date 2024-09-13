from uplogic.nodes import ULParameterNode
from mathutils import Vector, Matrix
import bpy
from bge import logic


class ResizeVectorNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.vec_in = Vector((0, 0, 0))
        self.OUT = self.add_output(self.get_2D_vec)
        self._to_size = 3
        self.funcs = [
            self.get_2D_vec,
            self.get_3D_vec,
            self.get_4D_vec
        ]

    @property
    def to_size(self):
        return self._to_size

    @to_size.setter
    def to_size(self, val):
        self.OUT._value_getter = self.funcs[val]
        self._to_size = val

    def get_2D_vec(self):
        return self.get_input(self.vec_in).to_2d()

    def get_3D_vec(self):
        return self.get_input(self.vec_in).to_3d()

    def get_4D_vec(self):
        return self.get_input(self.vec_in).to_4d()

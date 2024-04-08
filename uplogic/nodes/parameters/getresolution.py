from bge import render
from mathutils import Vector
from uplogic.nodes import ULParameterNode


class ULGetResolution(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.width = None
        self.height = None
        self.res = None
        self.WIDTH = self.add_output(self.get_width)
        self.HEIGHT = self.add_output(self.get_height)
        self.RES = self.add_output(self.get_res)

    def get_width(self):
        return render.getWindowWidth()

    def get_height(self):
        return render.getWindowHeight()

    def get_res(self):
        return Vector((self.width, self.height))

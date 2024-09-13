from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.utils.visualize import draw_cube


class ULDrawCube(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.color = None
        self.origin = None
        self.width = None
        self.use_volume_origin = False
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        origin = self.get_input(self.origin)
        width = self.get_input(self.width)
        color = self.get_input(self.color)
        origin = origin.copy()
        if self.use_volume_origin:
            offset = width * 0.5
            origin -= Vector((offset, offset, offset))
        draw_cube(origin, width, color)
        self._done = True

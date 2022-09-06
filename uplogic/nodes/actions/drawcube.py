from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.utils import is_invalid
from uplogic.utils import not_met
from uplogic.utils import draw_cube


class ULDrawCube(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.color = None
        self.origin = None
        self.width = None
        self.use_volume_origin = False

    def evaluate(self):
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        origin = self.get_input(self.origin)
        width = self.get_input(self.width)
        color = self.get_input(self.color)
        if is_invalid(origin, width, color):
            return
        origin = origin.copy()
        self._set_ready()
        if self.use_volume_origin:
            offset = width * 0.5
            origin -= Vector((offset, offset, offset))
        draw_cube(origin, width, color)
        self._set_value(True)

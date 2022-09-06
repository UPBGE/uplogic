from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.utils import is_invalid
from uplogic.utils import not_met
from uplogic.utils import draw_box


class ULDrawBox(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.color = None
        self.origin = None
        self.length = None
        self.width = None
        self.height = None
        self.use_volume_origin = False

    def evaluate(self):
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        origin = self.get_input(self.origin)
        length = self.get_input(self.length)
        width = self.get_input(self.width)
        height = self.get_input(self.height)
        color = self.get_input(self.color)
        if is_invalid(origin, length, width, height, color):
            return
        origin = origin.copy()
        self._set_ready()
        if self.use_volume_origin:
            origin -= Vector((width * 0.5, length * 0.5, height * 0.5))
        draw_box(origin, length, width, height, color)
        self._set_value(True)

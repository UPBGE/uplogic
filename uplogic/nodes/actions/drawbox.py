from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.utils.visuals import draw_box
from uplogic.nodes import ULOutSocket


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
        self.done = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        origin = self.get_input(self.origin)
        length = self.get_input(self.length)
        width = self.get_input(self.width)
        height = self.get_input(self.height)
        color = self.get_input(self.color)
        origin = origin.copy()
        if self.use_volume_origin:
            origin -= Vector((width * 0.5, length * 0.5, height * 0.5))
        draw_box(origin, length, width, height, color)
        self.done = True

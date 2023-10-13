from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bge.types import KX_GameObject


class ULSetLightColor(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.lamp = None
        self.color = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        light: KX_GameObject = self.get_input(self.lamp)
        color = self.get_input(self.color)
        if len(color) > 3:
            color = color[:-1]
        light = light.blenderObject.data
        light.color = color
        self.done = True

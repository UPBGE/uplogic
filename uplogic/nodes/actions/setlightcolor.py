from uplogic.nodes import ULActionNode
from bge.types import KX_GameObject


class ULSetLightColor(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.lamp = None
        self.color = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        light: KX_GameObject = self.get_input(self.lamp)
        color = self.get_input(self.color)
        if len(color) > 3:
            color = color[:-1]
        light = light.blenderObject.data
        light.color = color
        self._done = True

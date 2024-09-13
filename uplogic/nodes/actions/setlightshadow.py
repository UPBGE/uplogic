from uplogic.nodes import ULActionNode
from bge.types import KX_GameObject


class ULSetLightShadow(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.lamp = None
        self.use_shadow = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        light: KX_GameObject = self.get_input(self.lamp)
        use_shadow = self.get_input(self.use_shadow)
        light = light.blenderObject.data
        light.use_shadow = use_shadow
        self._done = True

from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import make_unique_light


class ULMakeUniqueLight(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.light = None
        self.done = None
        self._light = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.LIGHT = ULOutSocket(self, self.get_light)

    def get_done(self):
        return self.done

    def get_light(self):
        return self._light

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        self._light = make_unique_light(self.get_input(self.light))
        self.done = True

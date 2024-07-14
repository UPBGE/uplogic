from uplogic.nodes import ULActionNode
from uplogic.utils import make_unique_light


class ULMakeUniqueLight(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.light = None
        self._light = None
        self.OUT = self.add_output(self.get_done)
        self.LIGHT = self.add_output(self.get_light)

    def get_done(self):
        return self._done

    def get_light(self):
        return self._light

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        self._light = make_unique_light(self.get_input(self.light))
        self._done = True

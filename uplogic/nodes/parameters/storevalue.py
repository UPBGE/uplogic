from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULStoreValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.initialize = True
        self._value = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self._value

    def evaluate(self):
        self._set_ready()
        condition = self.get_input(self.condition)
        if condition or self.initialize:
            self.initialize = False
            self._value = self.get_input(self.value)

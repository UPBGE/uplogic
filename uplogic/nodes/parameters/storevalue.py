from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULStoreValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.initialize = True
        self.condition = None
        self._stored_value = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self._stored_value

    def evaluate(self):
        condition = self.get_input(self.condition)
        if self.initialize:
            self.initialize = False
            condition = True
        if not condition:
            return
        self._stored_value = self.get_input(self.value)

from uplogic.nodes import ULConditionNode, ULOutSocket
from bge.logic import getRealTime


class ULTimer(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.delta_time = None
        self._trigger = -1
        self.network = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.result

    def setup(self, network):
        self.network = network

    def evaluate(self):
        self.result = False
        condition = self.get_input(self.condition)
        delta_time = self.get_input(self.delta_time)
        now = getRealTime()

        if condition:
            self._trigger = now + delta_time
        if self._trigger == -1 or now < self._trigger:
            self.result = False
        else:
            self.result = True
            self._trigger = -1

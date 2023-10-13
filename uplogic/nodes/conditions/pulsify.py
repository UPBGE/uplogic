from uplogic.nodes import ULConditionNode, ULOutSocket
from bge.logic import getRealTime


class ULPulsify(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.delay = None
        self.result = False
        self._old_time = getRealTime()
        self._time = 0.0
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.result

    def evaluate(self):
        self.result = False
        now = getRealTime()
        if not self.get_input(self.condition):
            self._time = 0.0
            self._old_time = now
            return
        if self._time <= 0.0:
            self.result = True
            self._time = self.get_input(self.delay)
        self._time -= now - self._old_time
        self._old_time = now
        
from uplogic.nodes import ULConditionNode, ULOutSocket
from bge.logic import getRealTime


class ULBarrier(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.time = None
        self.consumed = False
        self.trigger = 0
        self.result = False
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.result

    def evaluate(self):
        self.result = False
        time = self.get_input(self.time)
        now = getRealTime()
        if self.get_input(self.condition):
            if not self.consumed:
                self.consumed = True
                self.trigger = now + time

            if now >= self.trigger:
                self.result = True

        else:
            self.result = False
            self.consumed = False

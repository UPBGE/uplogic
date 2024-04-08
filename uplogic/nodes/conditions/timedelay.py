from uplogic.nodes import ULConditionNode
from bge.logic import getRealTime


class ULTimeDelay(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.delay = None
        self.triggers = []
        self.result = False
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return self.result

    def evaluate(self):
        self.result = False
        condition = self.get_input(self.condition)
        delay = self.get_input(self.delay)
        now = getRealTime()
        if condition:
            self.triggers.append(now + delay)
        if not self.triggers:
            return
        t = self.triggers[0]
        if now >= t:
            self.result = True
            self.triggers.pop(0)
            return

from uplogic.nodes import ULConditionNode, ULOutSocket


class ULOnce(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.input_condition = None
        self.condition = False
        self.repeat = None
        self.reset_time = None
        self._consumed = False
        self._result = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self._result

    def evaluate(self):
        self._result = False
        condition = self.get_input(self.input_condition)
        repeat = self.get_input(self.repeat)
        if condition and not self.condition:
            self._result = True
            self.condition = condition
        if repeat:
            self.condition = condition

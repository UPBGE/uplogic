from uplogic.nodes import ULConditionNode


class ULOnNextTick(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.input_condition = None
        self._activated = 0
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        condition = self.get_input(self.input_condition)
        if self._activated == 1:
            if not condition:
                self._activated = 0
            return True
        elif condition:
            self._activated = 1
            return False
        elif self._activated == 0:
            return False

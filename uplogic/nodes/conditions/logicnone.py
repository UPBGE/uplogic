from uplogic.nodes import ULConditionNode, ULOutSocket


class ULNone(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.checked_value = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.get_input(self.checked_value) is None

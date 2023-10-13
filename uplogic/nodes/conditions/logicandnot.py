from uplogic.nodes import ULConditionNode, ULOutSocket


class ULAndNot(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition_a = None
        self.condition_b = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        ca = self.get_input(self.condition_a)
        cb = not self.get_input(self.condition_b)
        return ca and not cb

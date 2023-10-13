from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULNot(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        condition = self.get_input(self.condition)
        return not condition

from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.constants import LOGIC_OPERATORS


class ULCompare(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.operator = 'GREATER'
        self.param_a = None
        self.param_b = None
        self.threshold = 0.0
        self.RESULT = ULOutSocket(self, self.get_result)

    def get_result(self):
        a = self.get_input(self.param_a)
        b = self.get_input(self.param_b)
        threshold = self.get_input(self.threshold)
        operator = self.get_input(self.operator)
        if threshold is None:
            threshold = 0
        if threshold > 0 and abs(a - b) < threshold:
            a = b
        if operator is None:
            return
        return LOGIC_OPERATORS[operator](a, b)

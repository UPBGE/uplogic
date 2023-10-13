from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.constants import LOGIC_OPERATORS


class ULCompareVectors(ULConditionNode):
    def __init__(self, operator='GREATER'):
        ULConditionNode.__init__(self)
        self.operator = operator
        self.all = None
        self.threshold = None
        self.param_a = None
        self.param_b = None
        self.OUT = ULOutSocket(self, self.get_result)

    def get_result(self):
        a = self.get_input(self.param_a)
        b = self.get_input(self.param_b)
        all_values = self.get_input(self.all)
        operator = self.get_input(self.operator)
        threshold = self.get_input(self.threshold)
        return self.get_vec_val(
            operator,
            a,
            b,
            all_values,
            threshold
        )

    def get_vec_val(self, op, a, b, xyz, threshold):
        for ax in ['x', 'y', 'z']:
            av = getattr(a, ax)
            bv = getattr(b, ax)
            av = bv if abs(av - bv) < threshold else av
            if xyz[ax] and not LOGIC_OPERATORS[op](av, bv):
                return False
        return True

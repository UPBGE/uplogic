from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.constants import LOGIC_OPERATORS


class ULValueSwitch(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.conditon = None
        self.val_a = None
        self.val_b = None
        self.out_value = False
        self.VAL = ULOutSocket(self, self._get_out_value)

    def _get_out_value(self):
        condition = self.get_input(self.condition)
        return (
            self.get_input(self.val_a) if condition else self.get_input(self.val_b)
        )


class ULValueSwitchList(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.ca = True
        self.val_a = None
        self.cb = True
        self.val_b = None
        self.cc = True
        self.val_c = None
        self.cd = True
        self.val_d = None
        self.ce = True
        self.val_e = None
        self.cf = True
        self.val_f = None
        self.out_value = False
        self.VAL = ULOutSocket(self, self._get_out_value)

    def _get_out_value(self):
        if self.get_input(self.ca) is True:
            return self.get_input(self.val_a)
        if self.get_input(self.cb) is True:
            return self.get_input(self.val_b)
        if self.get_input(self.cc) is True:
            return self.get_input(self.val_c)
        if self.get_input(self.cd) is True:
            return self.get_input(self.val_d)
        if self.get_input(self.ce) is True:
            return self.get_input(self.val_e)
        if self.get_input(self.cf) is True:
            return self.get_input(self.val_f)
        else:
            return False


class ULValueSwitchListCompare(ULParameterNode):
    def __init__(self, operator='GREATER'):
        ULParameterNode.__init__(self)
        self.operator = operator
        self.p0 = None
        self.val_default = None
        self.pa = None
        self.val_a = None
        self.pb = None
        self.val_b = None
        self.pc = None
        self.val_c = None
        self.pd = None
        self.val_d = None
        self.pe = None
        self.val_e = None
        self.pf = None
        self.val_f = None
        self.RESULT = ULOutSocket(self, self.get_result)

    def is_none_if_not_eq_or_neq_operator(self, a, b):
        if self.operator > 1:  # eq and neq are valid for None
            if a is None or b is None:
                return True
            else:
                return False
        return False

    def get_result(self):
        p0 = self.get_input(self.p0)
        val_default = self.get_input(self.val_default)
        pa = self.get_input(self.pa)
        val_a = self.get_input(self.val_a)
        pb = self.get_input(self.pb)
        val_b = self.get_input(self.val_b)
        pc = self.get_input(self.pc)
        val_c = self.get_input(self.val_c)
        pd = self.get_input(self.pd)
        val_d = self.get_input(self.val_d)
        pe = self.get_input(self.pe)
        val_e = self.get_input(self.val_e)
        pf = self.get_input(self.pf)
        val_f = self.get_input(self.val_f)
        operator = self.get_input(self.operator)
        if self.is_none_if_not_eq_or_neq_operator(p0, pa):
            return
        if LOGIC_OPERATORS[operator](p0, pa):
            return val_a
        if self.is_none_if_not_eq_or_neq_operator(p0, pb):
            return
        if LOGIC_OPERATORS[operator](p0, pb):
            return val_b
        if self.is_none_if_not_eq_or_neq_operator(p0, pc):
            return
        if LOGIC_OPERATORS[operator](p0, pc):
            return val_c
        if self.is_none_if_not_eq_or_neq_operator(p0, pd):
            return
        if LOGIC_OPERATORS[operator](p0, pd):
            return val_d
        if self.is_none_if_not_eq_or_neq_operator(p0, pe):
            return
        if LOGIC_OPERATORS[operator](p0, pe):
            return val_e
        if self.is_none_if_not_eq_or_neq_operator(p0, pf):
            return
        if LOGIC_OPERATORS[operator](p0, pf):
            return val_f
        else:
            return val_default

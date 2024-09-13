from uplogic.nodes import ULParameterNode
from inspect import signature
from uplogic.utils.math import clamp


class MathNode(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value_a = 0.0
        self.value_b = 0.0
        self.value_c = 0.0
        self.clamp = False
        self.operator = None
        self.RESULT = self.add_output(self.get_result)

    def get_result(self):
        a = self.get_input(self.value_a)
        b = self.get_input(self.value_b)
        c = self.get_input(self.value_c)
        op = self.operator
        args = len(signature(op).parameters)
        if args == 1:
            result = self.operator(a)
        elif args == 2:
            result = self.operator(a, b)
        else:
            result = self.operator(a, b, c)
        return clamp(result) if self.clamp else result

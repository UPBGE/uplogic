from uplogic.nodes import ULParameterNode
import math


class ULAbsoluteValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.out_value = False
        self.OUT = self.add_output(self._get_out_value)

    def _get_out_value(self):
        value = self.get_input(self.value)
        return math.fabs(value)

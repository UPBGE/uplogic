from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULFormattedString(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.format_string = None
        self.value_a = None
        self.value_b = None
        self.value_c = None
        self.value_d = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        format_string = self.get_input(self.format_string)
        value_a = self.get_input(self.value_a)
        value_b = self.get_input(self.value_b)
        value_c = self.get_input(self.value_c)
        value_d = self.get_input(self.value_d)
        result = format_string.format(value_a, value_b, value_c, value_d)
        return result

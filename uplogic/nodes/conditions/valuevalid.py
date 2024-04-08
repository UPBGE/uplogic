from uplogic.nodes import ULConditionNode
from uplogic.utils import is_invalid


class ULValueValid(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.checked_value = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        value = self.get_input(self.checked_value)
        return not is_invalid(value)

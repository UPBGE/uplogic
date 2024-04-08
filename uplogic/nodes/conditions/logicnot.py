from uplogic.nodes import ULConditionNode


class ULNot(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        condition = self.get_input(self.condition)
        return not condition

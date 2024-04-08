from uplogic.nodes import ULConditionNode


class ULTrueFalse(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.state = None
        self.TRUE = self.add_output(self.get_true_value)
        self.FALSE = self.add_output(self.get_false_value)

    def get_true_value(self):
        return self.get_input(self.state)

    def get_false_value(self):
        return not self.get_input(self.state)

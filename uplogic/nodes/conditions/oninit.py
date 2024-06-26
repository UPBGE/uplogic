from uplogic.nodes import ULConditionNode


class ULOnInit(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return not self.network._initialized

from uplogic.nodes import ULConditionNode, ULOutSocket


class ULOnInit(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return not self.network._initialized

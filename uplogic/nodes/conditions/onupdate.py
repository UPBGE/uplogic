from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket

class ULOnUpdate(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return True

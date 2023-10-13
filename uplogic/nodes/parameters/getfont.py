from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULGetFont(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.font = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.get_input(self.font)

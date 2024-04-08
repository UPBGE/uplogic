from bge import logic
from uplogic.nodes import ULParameterNode


class ULGetTimeScale(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return logic.getTimeScale()

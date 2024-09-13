from bge import logic
from uplogic.nodes import ULActionNode


class ULSetTimeScale(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.timescale = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        timescale = self.get_input(self.timescale)
        logic.setTimeScale(timescale)
        self._done = True

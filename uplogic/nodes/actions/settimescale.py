from bge import logic
from uplogic.nodes import ULActionNode


class ULSetTimeScale(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.timescale = None
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        timescale = self.get_input(self.timescale)
        logic.setTimeScale(timescale)
        self.done = True

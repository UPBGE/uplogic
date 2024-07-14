from bge import render
from uplogic.nodes import ULActionNode


class ULSetVSync(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.vsync_mode = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        render.setVsync(self.vsync_mode)
        self._done = True

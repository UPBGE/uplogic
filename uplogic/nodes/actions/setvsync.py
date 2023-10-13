from bge import render
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetVSync(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.vsync_mode = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        render.setVsync(self.vsync_mode)
        self.done = True

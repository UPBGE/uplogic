from bge import render
from uplogic.nodes import ULActionNode


class ULSetFullscreen(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.use_fullscreen = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        use_fullscreen = self.get_input(self.use_fullscreen)
        render.setFullScreen(use_fullscreen)
        self._done = True

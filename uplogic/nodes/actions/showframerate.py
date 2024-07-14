from bge import render
from uplogic.nodes import ULActionNode


class ULShowFramerate(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.use_framerate = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        use_framerate = self.get_input(self.use_framerate)
        render.showFramerate(use_framerate)
        self._done = True

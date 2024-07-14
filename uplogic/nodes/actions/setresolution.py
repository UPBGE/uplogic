from bge import render
from uplogic.nodes import ULActionNode


class ULSetResolution(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.x_res = None
        self.y_res = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        x_res = self.get_input(self.x_res)
        y_res = self.get_input(self.y_res)
        render.setWindowSize(x_res, y_res)
        self._done = True

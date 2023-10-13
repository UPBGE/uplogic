from bge import render
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetResolution(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.x_res = None
        self.y_res = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        x_res = self.get_input(self.x_res)
        y_res = self.get_input(self.y_res)
        render.setWindowSize(x_res, y_res)
        self.done = True

from uplogic.nodes import ULActionNode
from uplogic.ui import Canvas


class ULCreateUICanvas(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self._canvas = None
        self.on_init = False
        self._done = False
        self.OUT = self.add_output(self._get_done)
        self.CANVAS = self.add_output(self._get_canvas)

    def _get_done(self):
        return self._done

    def _get_canvas(self):
        return self._canvas

    def evaluate(self):
        self._done = False
        if self.get_input(self.condition) or self.on_init:
            self._canvas = Canvas()
            self.on_init = False
            self._done = True

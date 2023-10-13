from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import Canvas


class ULCreateUICanvas(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self._canvas = None
        self._done = False
        self.OUT = ULOutSocket(self, self._get_done)
        self.CANVAS = ULOutSocket(self, self._get_canvas)

    def _get_done(self):
        return self._done

    def _get_canvas(self):
        return self._canvas

    def evaluate(self):
        self._done = False
        if not self.get_input(self.condition):
            return
        self._canvas = Canvas()
        self._done = True
        

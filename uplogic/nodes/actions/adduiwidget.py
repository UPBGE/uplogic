from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import Canvas
from uplogic.utils import not_met


class ULAddUIWidget(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent_widget = None
        self.child_widget = None
        self._done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        self._done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        self._set_ready()
        self.get_input(self.parent_widget).add_widget(self.get_input(self.child_widget))
        self._done = True
        

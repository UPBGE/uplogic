from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


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
        if not self.get_input(self.condition):
            return
        self.get_input(self.parent_widget).add_widget(self.get_input(self.child_widget))
        self._done = True
        

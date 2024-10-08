from uplogic.nodes import ULActionNode


class ULAddUIWidget(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent_widget = None
        self.child_widget = None
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        self.get_input(self.parent_widget).add_widget(self.get_input(self.child_widget))
        self._done = True
        

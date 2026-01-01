from uplogic.nodes import ULActionNode
from uplogic.ui import Widget


class MoveWidgetNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.widget: Widget = None
        self.mode = '0'
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if self.get_condition():
            widget: Widget = self.get_input(self.widget)
            operations = [
                widget.move_to_top,
                widget.move_up,
                widget.move_down,
                widget.move_to_bottom
            ]
            operations[int(self.mode)]()
            self._done = True

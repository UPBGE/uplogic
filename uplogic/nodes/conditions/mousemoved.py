from bge import events
from uplogic.nodes import ULConditionNode
from uplogic.input import mouse_moved


class ULMouseMoved(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False

    def evaluate(self):
        self._set_ready()
        if self.pulse:
            self._set_value(
                mouse_moved()
            )
        else:
            self._set_value(
                mouse_moved(tap=True)
            )

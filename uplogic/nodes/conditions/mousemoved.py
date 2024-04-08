from uplogic.nodes import ULConditionNode
from uplogic.input import mouse_moved


class ULMouseMoved(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        if self.pulse:
            return mouse_moved()
        return mouse_moved(tap=True)

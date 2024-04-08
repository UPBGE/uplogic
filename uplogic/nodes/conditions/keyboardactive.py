from uplogic.nodes import ULConditionNode
from bge.logic import keyboard


class ULKeyboardActive(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return len(keyboard.activeInputs) > 0

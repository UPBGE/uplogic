from uplogic.nodes import ULConditionNode
from bge.logic import keyboard


class ULKeyReleased(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.key_code = None
        self.network = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        keycode = self.get_input(self.key_code)
        keystat = keyboard.activeInputs[keycode]
        if self.pulse:
            return (
                keystat.released or
                keystat.inactive
            )
        return keystat.released

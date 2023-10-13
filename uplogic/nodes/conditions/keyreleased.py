from uplogic.nodes import ULConditionNode, ULOutSocket
from bge.logic import keyboard


class ULKeyReleased(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.key_code = None
        self.network = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        keycode = self.get_input(self.key_code)
        keystat = keyboard.activeInputs[keycode]
        if self.pulse:
            return (
                keystat.released or
                keystat.inactive
            )
        return keystat.released

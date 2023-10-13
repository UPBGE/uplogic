from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.input import key_tap
from uplogic.input import key_down
from uplogic.input import key_up


class ULKeyPressed(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.input_type = 1 if self.pulse else 0
        self.key_code = 0
        self.network = None
        self.OUT = ULOutSocket(self, self.get_pressed)

    def get_pressed(self):
        keycode = self.get_input(self.key_code)
        funcs = [key_tap, key_down, key_up]
        return funcs[self.input_type](keycode)

from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.input import gamepad_tap
from uplogic.input import gamepad_down
from uplogic.input import gamepad_up


class ULGamepadButton(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.input_type = 1 if self.pulse else 0
        self.button = 0
        self.index = None
        self._button = None
        self.BUTTON = ULOutSocket(self, self.get_button)
        self.initialized = False

    def get_button(self):
        index = self.get_input(self.index)
        funcs = [gamepad_tap, gamepad_down, gamepad_up]
        return funcs[self.input_type](self.button, index)

from bge import logic
from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULGamepadButtonUp(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.button = 0
        self.index = None
        self._last_value = False
        self._up_value = None
        self.BUTTON = ULOutSocket(self, self.get_button)
        self.initialized = False

    def get_button(self):
        pressed = False
        index = self.get_input(self.index)
        if logic.joysticks[index]:
            joystick = logic.joysticks[index]
        else:
            return False

        button_down = (
            True if
            self.button in joystick.activeButtons else
            False
        )

        if button_down != self._last_value and not button_down:
            if not self.pulse and not self.initialized:
                self.initialized = True
            pressed = True
        elif (pressed and self.initialized) or button_down:

            pressed = False
            self.initialized = False
        elif not (self.initialized and button_down) and pressed:
            pressed = True

        self._last_value = button_down
        return pressed

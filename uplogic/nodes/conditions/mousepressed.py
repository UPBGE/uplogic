from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.input import mouse_tap
from uplogic.input import mouse_down
from uplogic.input import mouse_up


class ULMousePressed(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.input_type = 1 if self.pulse else 0
        self.mouse_button_code = None
        self.OUT = ULOutSocket(self, self.get_pressed)

    def get_pressed(self):
        mouse_button = self.get_input(self.mouse_button_code)
        funcs = [mouse_tap, mouse_down, mouse_up]
        return funcs[self.input_type](mouse_button)

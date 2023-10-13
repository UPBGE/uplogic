from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.input import record_keyboard


class ULKeyLogger(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.only_characters = None
        self.PRESSED = ULOutSocket(self, self.get_pressed)
        self.CHARACTER = ULOutSocket(self, self.get_character)
        self.KEYCODE = ULOutSocket(self, self.get_keycode)

    def get_pressed(self):
        return self.scan()[0]

    def get_keycode(self):
        return self.scan()[1]

    def get_character(self):
        return self.scan()[2]

    def scan(self):
        data = record_keyboard(not self.get_input(self.only_characters))
        return data

    def reset(self):
        super().reset()
        self._key_logged = False
        self._key_code = None
        self._character = None

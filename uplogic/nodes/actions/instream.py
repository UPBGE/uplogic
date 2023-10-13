from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bge import events
from bge.logic import keyboard


class ULKeyLogger(ULActionNode):
    '''DEPRECATED
    This node has been moved to `parameters`, this is for legacy support.
    '''
    def __init__(self, pulse=False):
        ULActionNode.__init__(self)
        self.condition = None
        self.pulse = pulse
        self._key_logged = None
        self._key_code = None
        self._character = None
        self.KEY_LOGGED = ULOutSocket(self, self.get_key_logged)
        self.KEY_CODE = ULOutSocket(self, self.get_key_code)
        self.CHARACTER = ULOutSocket(self, self.get_character)

    def get_key_logged(self):
        return self._key_logged

    def get_key_code(self):
        return self._key_code

    def get_character(self):
        return self._character

    def reset(self):
        super().reset()
        self._key_logged = False
        self._key_code = None
        self._character = None

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        network = self.network
        keyboard_status = keyboard.inputs.copy()
        left_shift_status = keyboard_status[events.LEFTSHIFTKEY].active
        right_shift_status = keyboard_status[events.RIGHTSHIFTKEY].active
        shift_down = (
            left_shift_status or
            right_shift_status or
            network.capslock_pressed
        )
        active_events = keyboard.activeInputs.copy()
        active = (
            'active' if self.pulse
            else 'activated'
        )
        for keycode in active_events:
            event = active_events[keycode]
            if getattr(event, active):
                # something has been pressed
                self._character = events.EventToCharacter(
                    event.type,
                    shift_down
                )
                self._key_code = keycode
                self._key_logged = True

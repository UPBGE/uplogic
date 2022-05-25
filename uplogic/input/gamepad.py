from bge import logic
from mathutils import Vector
from uplogic.utils import debug


XBOX = {
    'A': 0,
    'B': 1,
    'X': 2,
    'Y': 3,
    'SELECT': 4,
    'BACK': 4,
    'START': 6,
    'MENU': 6,
    'LS': 7,
    'L3': 7,
    'RS': 8,
    'R3': 8,
    'LB': 9,
    'RB': 10,
    'DPADUP': 11,
    'DPADDOWN': 12,
    'DPADLEFT': 13,
    'DPADRIGHT': 14,
    'RT': 5,
    'LT': 4
}
SONY = {
    'X': 0,
    'CROSS': 0,
    'CIRCLE': 1,
    'SQUARE': 2,
    'TRIANGLE': 3,
    'SELECT': 4,
    'SHARE': 4,
    'START': 6,
    'MENU': 6,
    'L3': 7,
    'R3': 8,
    'L1': 9,
    'R1': 10,
    'DPADUP': 11,
    'DPADDOWN': 12,
    'DPADLEFT': 13,
    'DPADRIGHT': 14,
    'R2': 5,
    'L2': 4
}

LS = 'LEFTSTICK'
RS = 'RIGHTSTICK'

STICKS = {
    LS: [0, 1],
    RS: [2, 3]
}


_active_buttons = {}
_active_axis = {}


def gamepad_button(
    button: int,
    idx: int = 0,
    tap: int = False,
    released: int = False
) -> bool:
    '''Retrieve button value.\n
    Not intended for manual use.
    '''
    global _active_buttons
    if logic.joysticks[idx] is None:
        return False
    gamepad = logic.joysticks[idx]
    state = button in gamepad.activeButtons
    if tap or released:
        if released:
            tap_cond = _active_buttons.get(button, False)
            _active_buttons[button] = state
            return not state and tap_cond
        tap_cond = not _active_buttons.get(button, False)
        _active_buttons[button] = state
        return state and tap_cond
    _active_buttons[button] = state
    return state


def gamepad_axis(
    axis: int,
    idx: int = 0,
    tap: bool = False,
    released: bool = False,
    threshold: float = .07
) -> float:
    '''Retrieve axis value.\n
    Not intended for manual use.
    '''
    global _active_axis
    if logic.joysticks[idx] is None:
        return 0.0
    gamepad = logic.joysticks[idx]
    if released:
        val = gamepad.axisValues[axis]
        if _active_axis.get(axis, 0) != 0 and val == 0:
            _active_axis[axis] = val
            return 1.0
        else:
            _active_axis[axis] = val
            return 0.0
    if tap:
        if _active_axis.get(axis, 0) == 0:
            val = gamepad.axisValues[axis]
            _active_axis[axis] = val
            return val if abs(val) >= threshold else 0
        else:
            _active_axis[axis] = gamepad.axisValues[axis]
            return 0.0
    val = gamepad.axisValues[axis]
    _active_axis[axis] = val
    return val if abs(val) >= threshold else 0


def gamepad_stick(
    stick: str = LS,
    idx: int = 0,
    threshold: float = .07
) -> set:
    '''Retrieve stick values.

    :param stick: which stick to use.
    can bei either `LS` or `RS` from `uplogic.input`.
    :param idx: gamepad index (default = 0).
    :param threshold: minimum value for each axis to be valid.

    :returns: set `(x, y)`
    '''
    xaxis = STICKS[stick][0]
    yaxis = STICKS[stick][1]
    return Vector((
        gamepad_axis(xaxis, idx, threshold=threshold),
        gamepad_axis(yaxis, idx, threshold=threshold)
    ))


def gamepad_tap(
    button: str,
    idx: int = 0,
    layout: dict = XBOX
) -> float or bool:
    '''Detect button tap.

    :param button: button name as `str` (e.g. `'START'`)
    :param idx: gamepad index (default = 0).
    :param layout: gamepad layout,
    can be either `XBOX` or `SONY` from `uplogic.input`.

    :returns: float or boolean
    '''
    btn_idx = layout[button]
    if button in ['R2', 'L2', 'RT', 'LT']:
        return gamepad_axis(btn_idx, idx, True)
    else:
        return gamepad_button(btn_idx, idx, True)


def gamepad_down(
    button: str,
    idx: int = 0,
    layout: dict = XBOX
) -> float or bool:
    '''Detect button held down.

    :param button: button name as `str` (e.g. `'START'`)
    :param idx: gamepad index (default = 0).
    :param layout: gamepad layout,
    can be either `XBOX` or `SONY` from `uplogic.input`.

    :returns: float or boolean
    '''
    btn_idx = layout[button]
    if button in ['R2', 'L2', 'RT', 'LT']:
        return gamepad_axis(btn_idx, idx)
    else:
        return gamepad_button(btn_idx, idx)


def gamepad_up(
    button: str,
    idx: int = 0,
    layout: dict = XBOX
) -> float or bool:
    '''Detect button released.

    :param button: button name as `str` (e.g. `'START'`)
    :param idx: gamepad index (default = 0).
    :param layout: gamepad layout,
    can be either `XBOX` or `SONY` from `uplogic.input`.

    :returns: float or boolean
    '''
    btn_idx = layout[button]
    if button in ['R2', 'L2', 'RT', 'LT']:
        return gamepad_axis(btn_idx, idx, True, True)
    else:
        return gamepad_button(btn_idx, idx, True, True)


class ULGamePad():

    def __init__(
        self,
        idx: int = 0,
        layout: dict = XBOX
    ) -> None:
        self.idx = idx
        self.layout = layout
        if not logic.joysticks[idx]:
            debug(f'No Joystick found at index: {idx}')
        self.joystick = logic.joysticks[idx]

    def button_down(self, button: str):
        return gamepad_down(button, self.idx, self.layout)
        
    def button_tap(self, button: str):
        return gamepad_tap(button, self.idx, self.layout)

    def button_up(self, button: str):
        return gamepad_up(button, self.idx, self.layout)

    def sticks(self, stick: str = LS, threshold: float = 0.07):
        return gamepad_stick(stick, self.idx, threshold)
    
    def vibrate(self, strength: tuple = (.5, .5), time: float = 1.0):
        if not self.joystick.hasVibration:
            debug('Joystick at index {} has no vibration!'.format(self.idx))
            return
        self.joystick.strengthLeft = strength[0]
        self.joystick.strengthRight = strength[1]
        self.joystick.duration = int(round(time * 1000))

        self.joystick.startVibration()
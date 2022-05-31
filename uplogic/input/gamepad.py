from bge import logic
from bge.types import KX_GameObject as GameObject
from math import pi
from mathutils import Vector
from uplogic.utils import debug
from uplogic.utils import interpolate
from uplogic.events import schedule_callback


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
"""Buttons in [`A`, `B`, `X`, `Y`, `SELECT`, `BACK`, `START`, `MENU`, `LS`,
`L3`, `RS`, `R3`, `LB`, `RB`, `DPADUP`, `DPADDOWN`, `DPADLEFT`, `DPADRIGHT`,
`RT`, `LT`]"""


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
"""Buttons in [`X`, `CROSS`, `CIRCLE`, `SQUARE`, `TRIANGLE`, `SELECT`, `SHARE`,
`START`, `MENU`, `L3`, `R3`, `L1`, `R1`, `DPADUP`, `DPADDOWN`, `DPADLEFT`,
`DPADRIGHT`, `R2`, `L2`]"""


LS = 'LS'
RS = 'RS'

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


def gamepad_trigger(
    trigger: str = 'LT',
    idx: int = 0,
    threshold: float = .07
) -> float:
    """Retrieve gamepad trigger values.

    :param `trigger`: Whether to use the left or right trigger;
    `str` in [`'LT'`, `'RT'`].
    :param `idx`: index of the gamepad.
    :param `threshold`: Only detect values higher than the threshold.

    :returns: Intensity of the selected trigger.
    """
    return gamepad_axis(4 if trigger == 'LT' else 5, idx, threshold=threshold)


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


def gamepad_vibrate(idx: int = 0, strength: tuple = (.5, .5), time: float = 1.0):
    """Start the vibrators of the gamepad if available.

    :param `idx`: 
    """
    joystick = logic.joysticks[idx]
    if not joystick or not joystick.hasVibration:
        debug(f'Joystick at index {idx} has no vibration!')
    joystick.strengthLeft = strength[0]
    joystick.strengthRight = strength[1]
    joystick.duration = int(round(time * 1000))

    joystick.startVibration()


class ULGamePad():
    """Wrapper class for a controller. The index determines which connected
    gamepad to use, the layout determines whether to use XBox or Sony button
    naming.
    
    :param `idx`: Which gamepad to use.
    :param `layout`: Layout determining button names; `str` in [`'XBOX'`,
    `'SONY'`].
    """

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


class ULGamepadLook():
    """Automatically track the mouse movement and translate it to a rotate a
    body and optionally a head.

    This component can be activated/deactivated at any time to keep performance
    up.
    
    :param `obj`: Main object to rotate around the object's Z axis.
    :param `head`: Head object to rotate around the object's X/Y axis.
    :param `sensitivity`: Translation factor of mouse movement to rotation.
    :param `use_cap_x`: Whether to use capping on the mouse X movement (Z axis
    rotation).
    :param `cap_x`: Minimum and Maximum amount of rotation on the Z axis.
    :param `use_cap_y`: Whether to use capping on the mouse Y movement (X/Y axis
    rotation).
    :param `cap_y`: Minimum and Maximum amount of rotation on the X/Y axis.
    :param `invert`: Whether to use inverted values for mous X/Y movement.
    :param `smoothing`: Amount of movement smoothing.
    :param `local`: Whether to use local transform for the body object.
    :param `front`: Front axis (traditionally in blender, Y is front).
    :param `active`: Whether to start this component in active or inactive mode
    (can be changed later).
    """
    def __init__(
        self,
        obj: GameObject,
        head: GameObject = None,
        sensitivity: float = .05,
        use_cap_x: bool = False,
        cap_x: tuple = (0, 0),
        use_cap_y: bool = False,
        cap_y: tuple = (-89, 89),
        invert: tuple = (True, True),
        smoothing: float = 0.0,
        local: bool = True,
        front: int = 1,
        idx: int = 0,
        stick: int = 'RS',
        threshold: float = 0.07,
        exponent: float = 2.3,
        active=True
    ) -> None:
        self.obj = obj
        self.head = head if head else obj
        self._defaults = [
            obj.localOrientation.copy(),
            head.localOrientation.copy()
            if head else
            obj.localOrientation.copy()]
        self.sensitivity = sensitivity
        self.use_cap_x = use_cap_x
        self.cap_x = cap_x
        self.use_cap_y = use_cap_y
        self.cap_y = cap_y
        self.invert = invert
        self.smoothing = smoothing
        self.initialized = False
        self.front = front
        self._x = 0
        self._y = 0
        self._active = False
        self.local = local
        self.reset_factor = 0
        self.stick = stick
        self.threshold = threshold
        self.exponent = exponent
        self.joystick = logic.joysticks[idx]
        self.active = active

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, val):
        scene = logic.getCurrentScene()
        if val and self.update not in scene.pre_draw and self.joystick:
            scene.pre_draw.append(self.update)
        elif not val and self.update in scene.pre_draw:
            self.initialized = False
            scene.pre_draw.remove(self.update)
        self._active = val

    @property
    def rotation(self):
        return self.obj.worldOrientation, self.head.worldOrientation

    @rotation.setter
    def rotation(self, val):
        self.obj.worldOrientation = val[0]
        self.head.worldOrientation = val[1]

    def stop(self):
        self.active = False
        self.initialized = False

    def disable(self):
        self.active = False

    def enable(self):
        self.active = True

    def reset(self, factor=1):
        if factor < 1:
            self.active = False
            if self.reset_factor < 1:
                self.obj.localOrientation = self.obj.localOrientation.lerp(self._defaults[0], factor)
                self.head.localOrientation = self.head.localOrientation.lerp(self._defaults[1], factor)
                self.reset_factor = interpolate(self.reset_factor, 1, factor)
                schedule_callback(self.reset, arg=factor)
            else:
                self.reset_factor = 0
                self.reset()
        else:
            self.obj.localOrientation = self._defaults[0]
            self.head.localOrientation = self._defaults[1]

    def update(self):
        game_object_x = self.obj
        game_object_y = self.head
        sensitivity = self.sensitivity * 10
        cap_x = self.cap_x
        lowercapX = cap_x[0] * pi / 180
        uppercapX = cap_x[1] * pi / 180
        cap_y = self.cap_y
        lowercapY = cap_y[0] * pi / 180
        uppercapY = cap_y[1] * pi / 180
        invert = self.invert
        smooth = 1 - (self.smoothing * .99)
        joystick = self.joystick
        raw_values = joystick.axisValues
        if self.stick == 'RS':
            x, y = raw_values[2], raw_values[3]
        elif self.stick == 'LS':
            x, y = raw_values[0], raw_values[1]
        neg_x = -1 if x < 0 else 1
        neg_y = -1 if y < 0 else 1

        threshold = self.threshold
        if -threshold < x < threshold:
            x = 0
        else:
            x = abs(x) ** self.exponent

        if -threshold < y < threshold:
            y = 0
        else:
            y = abs(y) ** self.exponent

        x *= neg_x
        y *= neg_y

        self._x = x = interpolate(self._x, -x if invert[0] else x, smooth)
        self._y = y = interpolate(self._y, -y if invert[1] else y, smooth)
        if self._x == self._y == 0:
            self.done = True
            return

        x *= sensitivity
        y *= sensitivity
        if self.use_cap_x:
            objectRotation = game_object_x.localOrientation.to_euler()

            if objectRotation.z + x > uppercapX:
                x = 0
                objectRotation.z = uppercapX
                game_object_x.localOrientation = objectRotation

            if objectRotation.z + x < lowercapX:
                x = 0
                objectRotation.z = lowercapX
                game_object_x.localOrientation = objectRotation

        game_object_x.applyRotation((0, 0, x), self.local)

        rot_axis = 1 - self.front
        if self.use_cap_y:
            objectRotation = game_object_y.localOrientation.to_euler()

            if objectRotation[rot_axis] + y > uppercapY:
                objectRotation[rot_axis] = uppercapY
                game_object_y.localOrientation = objectRotation
                y = 0

            if objectRotation[rot_axis] + y < lowercapY:
                objectRotation[rot_axis] = lowercapY
                game_object_y.localOrientation = objectRotation
                y = 0

        rot = [0, 0, 0]
        rot[1-self.front] = y
        game_object_y.applyRotation((*rot, ), True)
        self.done = True

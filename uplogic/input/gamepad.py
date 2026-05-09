'''Gamepad/joystick input helpers for uplogic.

Provides button, axis, stick, and trigger query functions and the
:class:`Gamepad` and :class:`GamepadLook` component classes.
Both XBOX and Sony controller layouts are supported via the :data:`XBOX`
and :data:`SONY` button-name dictionaries.
'''
from bge import logic
from bge.types import KX_GameObject as GameObject
from math import pi
from mathutils import Vector
from uplogic.utils.math import interpolate
from uplogic.events import schedule_callback
from uplogic import console


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
    'RT': 15,
    'LT': 16
}
'''Button-name to index mapping for Xbox-style controllers. Valid keys: ``"A"``, ``"B"``, ``"X"``, ``"Y"``, ``"SELECT"``, ``"BACK"``, ``"START"``, ``"MENU"``, ``"LS"``, ``"L3"``, ``"RS"``, ``"R3"``, ``"LB"``, ``"RB"``, ``"DPADUP"``, ``"DPADDOWN"``, ``"DPADLEFT"``, ``"DPADRIGHT"``, ``"RT"``, ``"LT"``.'''


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
    'R2': 15,
    'L2': 16
}
'''Button-name to index mapping for Sony (PlayStation) controllers. Valid keys: ``"X"``, ``"CROSS"``, ``"CIRCLE"``, ``"SQUARE"``, ``"TRIANGLE"``, ``"SELECT"``, ``"SHARE"``, ``"START"``, ``"MENU"``, ``"L3"``, ``"R3"``, ``"L1"``, ``"R1"``, ``"DPADUP"``, ``"DPADDOWN"``, ``"DPADLEFT"``, ``"DPADRIGHT"``, ``"R2"``, ``"L2"``.'''


LS = 15
'''Axis index constant for the left analogue stick (``15``).'''
RS = 16
'''Axis index constant for the right analogue stick (``16``).'''

STICKS = {
    LS: [0, 1],
    RS: [2, 3]
}


_active_buttons = [{} for x in logic.joysticks]
_active_axis = [{} for x in logic.joysticks]


def gamepad_button(
    button: int,
    idx: int = 0,
    tap: int = False,
    released: int = False
) -> bool:
    '''Query a single button state on the joystick at *idx*.

    Not intended for direct use; call :func:`gamepad_tap`, :func:`gamepad_down`,
    or :func:`gamepad_up` instead.

    :param button: Button index.
    :param idx: Joystick device index (default ``0``).
    :param tap: When ``True``, return ``True`` only on the activation frame.
    :param released: When ``True``, return ``True`` only on the release frame.
    :returns: ``True`` when the button matches the requested state, ``False``
        when no joystick is connected at *idx*.
    '''
    global _active_buttons
    if logic.joysticks[idx] is None:
        return False
    gamepad = logic.joysticks[idx]
    state = button in gamepad.activeButtons
    if tap or released:
        if released:
            tap_cond = _active_buttons[idx].get(button, False)
            _active_buttons[idx][button] = state
            return not state and tap_cond
        tap_cond = not _active_buttons[idx].get(button, False)
        _active_buttons[idx][button] = state
        return state and tap_cond
    return state


def gamepad_axis(
    axis: int,
    idx: int = 0,
    tap: bool = False,
    released: bool = False,
    threshold: float = .07
) -> float:
    '''Query a single axis value on the joystick at *idx*.

    Not intended for direct use; call :func:`gamepad_stick` or
    :func:`gamepad_trigger` instead.

    :param axis: Axis index (indices 15/16 are remapped internally).
    :param idx: Joystick device index.
    :param tap: When ``True``, return the value only on the first non-zero frame.
    :param released: When ``True``, return ``1.0`` on the frame the axis returns
        to zero.
    :param threshold: Values with absolute magnitude below this are treated as
        zero.
    :returns: Axis float value, or ``0.0`` when no joystick is connected.
    '''
    if axis > 5:
        axis -= 11  # for indices 15, 16
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
            val = val if abs(val) >= threshold else 0
            _active_axis[axis] = val
            return val if abs(val) >= threshold else 0
        else:
            val = gamepad.axisValues[axis]
            _active_axis[axis] = val if abs(val) >= threshold else 0
            return 0.0
    val = gamepad.axisValues[axis]
    _active_axis[axis] = val
    return val if abs(val) >= threshold else 0


def gamepad_trigger(
    trigger: str = 'LT',
    idx: int = 0,
    threshold: float = .1
) -> float:
    '''Return the intensity of a trigger on the gamepad at *idx*.

    :param trigger: Which trigger to read — ``"LT"`` for left, ``"RT"`` for
        right.
    :param idx: Joystick device index.
    :param threshold: Minimum value to report; readings below this return
        ``0.0``.
    :returns: Trigger intensity as a ``float`` in the range ``[0, 1]``.
    '''
    return gamepad_axis(15 if trigger == 'LT' else 16, idx, threshold=threshold)


def gamepad_stick(
    stick: str = LS,
    idx: int = 0,
    threshold: float = .1,
    invert: tuple = (False, True)
) -> Vector:
    '''Return the X/Y deflection of an analogue stick as a 2D vector.

    :param stick: Which stick to query — use :data:`LS` or :data:`RS`, or the
        strings ``"LS"``/``"RS"``.
    :param idx: Joystick device index.
    :param threshold: Per-axis dead-zone; values below this magnitude are
        clamped to zero.
    :param invert: ``(invert_x, invert_y)`` flags; by default Y is inverted to
        match typical first-person conventions.
    :returns: :class:`mathutils.Vector` of ``(x, y)`` in the range ``[-1, 1]``.
    '''
    if stick == 'LS':
        stick = LS
    elif stick == 'RS':
        stick = RS
    xaxis = STICKS[stick][0]
    yaxis = STICKS[stick][1]
    return Vector((
        gamepad_axis(xaxis, idx, threshold=threshold) * (-1 if invert[0] else 1),
        gamepad_axis(yaxis, idx, threshold=threshold) * (-1 if invert[1] else 1)
    ))


def gamepad_tap(
    button: str,
    idx: int = 0,
    layout: dict = XBOX
) -> float or bool:
    '''Return ``True`` on the single frame a button or trigger is first activated.

    :param button: Button name string (e.g. ``"A"``, ``"START"``) or integer
        index.
    :param idx: Joystick device index.
    :param layout: Button-name dictionary — :data:`XBOX` or :data:`SONY`.
    :returns: ``True`` on the activation frame.
    '''
    if isinstance(button, str):
        button = layout.get(button.upper(), button.upper())
    if button in [15, 16]:
        return gamepad_axis(button, idx, True)
    else:
        return gamepad_button(button, idx, True)


def gamepad_down(
    button: str,
    idx: int = 0,
    layout: dict = XBOX
) -> float or bool:
    '''Return ``True`` while a button or trigger is held down.

    :param button: Button name string or integer index.
    :param idx: Joystick device index.
    :param layout: Button-name dictionary — :data:`XBOX` or :data:`SONY`.
    :returns: ``True`` while the button is active, or the trigger float value.
    '''
    btn_idx = layout.get(button, button)
    if button in [15, 16, 'R2', 'L2', 'RT', 'LT']:
        return gamepad_axis(btn_idx, idx)
    else:
        return gamepad_button(btn_idx, idx)


def gamepad_up(
    button: str,
    idx: int = 0,
    layout: dict = XBOX
) -> float or bool:
    '''Return ``True`` on the single frame a button or trigger is released.

    :param button: Button name string or integer index.
    :param idx: Joystick device index.
    :param layout: Button-name dictionary — :data:`XBOX` or :data:`SONY`.
    :returns: ``True`` on the release frame.
    '''
    btn_idx = layout.get(button, button)
    if button in [15, 16, 'R2', 'L2', 'RT', 'LT']:
        return gamepad_axis(btn_idx, idx, True, True)
    else:
        return gamepad_button(btn_idx, idx, True, True)


def gamepad_vibrate(idx: int = 0, strength: tuple = (.5, .5), time: float = 1.0):
    '''Start the vibration motors on the gamepad at *idx*.

    Does nothing and logs a debug message when the device has no vibration
    support.

    :param idx: Joystick device index.
    :param strength: ``(left_motor, right_motor)`` intensities in ``[0, 1]``.
    :param time: Vibration duration in seconds.
    '''
    joystick = logic.joysticks[idx]
    if not joystick or not joystick.hasVibration:
        console.debug(f'Joystick at index {idx} has no vibration!')
    joystick.strengthLeft = strength[0]
    joystick.strengthRight = strength[1]
    joystick.duration = int(round(time * 1000))

    joystick.startVibration()


class Gamepad():
    '''Stateful wrapper around a single gamepad/joystick device.

    :param idx: Index of the joystick to use (default ``0``).
    :param layout: Button-name mapping — use :data:`XBOX` or :data:`SONY`.
    '''

    _deprecated = False

    def __init__(
        self,
        idx: int = 0,
        layout: dict = XBOX
    ) -> None:
        if self._deprecated:
            console.warning('Warning: ULGamePad class will be renamed to "Gamepad" in future releases!')
        self.idx = idx
        self.layout = layout
        if not logic.joysticks[idx]:
            console.error(f'No Joystick found at index: {idx}')
        self.device = logic.joysticks[idx]

    def button_down(self, button: str):
        '''Return ``True`` while *button* is held down.

        :param button: Button name string (e.g. ``"A"``) or integer index.
        '''
        return gamepad_down(button, self.idx, self.layout)

    def button_tap(self, button: str):
        '''Return ``True`` on the single frame *button* is first pressed.

        :param button: Button name string or integer index.
        '''
        return gamepad_tap(button, self.idx, self.layout)

    def button_up(self, button: str):
        '''Return ``True`` on the single frame *button* is released.

        :param button: Button name string or integer index.
        '''
        return gamepad_up(button, self.idx, self.layout)

    def sticks(self, stick: str = LS, threshold: float = 0.07):
        '''Return the X/Y deflection of an analogue stick.

        :param stick: :data:`LS` or :data:`RS`.
        :param threshold: Per-axis dead-zone magnitude.
        :returns: :class:`mathutils.Vector` of ``(x, y)``.
        '''
        return gamepad_stick(stick, self.idx, threshold)

    def rumble(self, strength: tuple = (.5, .5), time: float = 1.0):
        '''Activate the vibration motors.

        :param strength: ``(left_motor, right_motor)`` intensities in ``[0, 1]``.
        :param time: Duration in seconds.
        '''
        if not self.device.hasVibration:
            console.debug('Joystick at index {} has no vibration!'.format(self.idx))
            return
        self.device.strengthLeft = strength[0]
        self.device.strengthRight = strength[1]
        self.device.duration = int(round(time * 1000))

        self.device.startVibration()

    def vibrate(self, strength: tuple = (.5, .5), time: float = 1.0):
        '''Alias for :meth:`rumble`.'''
        self.rumble(strength, time)


class ULGamePad(Gamepad):
    '''[DEPRECATED] Use :class:`Gamepad` instead.'''
    _deprecated = True


class GamepadLook():
    '''Gamepad-stick-driven first-person look controller.

    Translates right (or left) stick movement into rotations on a body object
    (Z axis) and an optional head object (X/Y axis). The controller can be
    toggled at any time via :attr:`active`.

    :param obj: Primary object to rotate around the Z axis.
    :param head: Secondary object for vertical rotation; defaults to *obj*.
    :param sensitivity: Stick deflection to rotation scale factor.
    :param use_cap_x: Enable rotation clamping on the Z axis.
    :param cap_x: ``(min, max)`` Z-axis rotation limits in degrees.
    :param use_cap_y: Enable rotation clamping on the X/Y axis.
    :param cap_y: ``(min, max)`` X/Y-axis rotation limits in degrees.
    :param invert: ``(invert_x, invert_y)`` flags for each axis.
    :param smoothing: Smoothing factor in ``[0, 1)``.
    :param local: When ``True``, apply rotations in local space.
    :param front: Front axis index (``1`` = Y, Blender default).
    :param idx: Joystick device index.
    :param stick: Which stick to use — ``"RS"`` or ``"LS"``.
    :param threshold: Stick dead-zone magnitude.
    :param exponent: Power curve applied to raw stick values for finer control
        near centre.
    :param active: Whether to start the component active.
    '''
    _deprecated = False
    def __init__(
        self,
        obj: GameObject,
        head: GameObject = None,
        sensitivity: float = .05,
        use_cap_x: bool = False,
        cap_x: tuple = (0, 0),
        use_cap_y: bool = False,
        cap_y: tuple = (-89, 89),
        invert: tuple = (False, False),
        smoothing: float = 0.0,
        local: bool = True,
        front: int = 1,
        idx: int = 0,
        stick: int = 'RS',
        threshold: float = 0.07,
        exponent: float = 2.3,
        active=True
    ) -> None:
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULGamepadLook class will be renamed to "GamepadLook" in future releases!')
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
        '''Whether the per-frame update is registered. Setting to ``False`` removes the update from the scene pre-draw list.'''
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
        '''Tuple of ``(body_world_orientation, head_world_orientation)``. Setting writes both orientations simultaneously.'''
        return self.obj.worldOrientation, self.head.worldOrientation

    @rotation.setter
    def rotation(self, val):
        self.obj.worldOrientation = val[0]
        self.head.worldOrientation = val[1]

    def stop(self):
        '''Deactivate the controller and reset :attr:`initialized`.'''
        self.active = False
        self.initialized = False

    def disable(self):
        '''Deactivate the controller (alias for setting :attr:`active` to ``False``).'''
        self.active = False

    def enable(self):
        '''Activate the controller (alias for setting :attr:`active` to ``True``).'''
        self.active = True

    def reset(self, factor=1):
        '''Restore both objects to their original orientations captured at construction.

        :param factor: When ``< 1``, lerp smoothly each frame via
            :func:`~uplogic.events.schedule_callback`; when ``1``, snap immediately.
        '''
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
        '''Per-frame update: read stick values, apply dead-zone, smoothing, power curve, and caps, then rotate both objects. Called automatically via the scene pre-draw list.'''
        game_object_x = self.obj
        game_object_y = self.head
        sensitivity = self.sensitivity
        cap_x = self.cap_x
        cap_y = self.cap_y
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

        self._x = x = interpolate(self._x, x if invert[0] else -x, smooth)
        self._y = y = interpolate(self._y, y if invert[1] else -y, smooth)
        if self._x == self._y == 0:
            return

        x *= sensitivity
        y *= sensitivity
        if self.use_cap_x:
            lowercapX = cap_x[0] * pi / 180
            uppercapX = cap_x[1] * pi / 180
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
            lowercapY = cap_y[0] * pi / 180
            uppercapY = cap_y[1] * pi / 180
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


class ULGamepadLook(GamepadLook):
    '''[DEPRECATED] Use :class:`GamepadLook` instead.'''
    _deprecated = True


def gamepad_active(idx) -> bool:
    '''Return ``True`` when the joystick at *idx* has any active buttons or
    significant axis deflection.

    :param idx: Joystick device index.
    :returns: ``True`` if any button is pressed or any axis exceeds ±0.1.
    '''
    if logic.joysticks[idx]:
        joystick = logic.joysticks[idx]
    else:
        return False
    axis_active = False
    for x in joystick.axisValues:
        if x < -.1 or x > .1:
            axis_active = True
            break
    return (
        len(joystick.activeButtons) > 0 or
        axis_active
    )

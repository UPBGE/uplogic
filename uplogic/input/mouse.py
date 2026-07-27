'''Mouse input helpers for uplogic. Wraps ``bge.logic.mouse.inputs`` into boolean query functions and provides :class:`Mouse` and :class:`MouseLook` component classes.
'''
from math import pi
from bge import logic
from bge import events
from bge import render
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.utils.math import interpolate
from uplogic.utils.math import clamp
from uplogic.events import schedule_callback
from uplogic import console


MOUSE_EVENTS = logic.mouse.inputs
'''Reference to ``bge.logic.mouse.inputs``.'''

LMB = events.LEFTMOUSE
'''Left mouse button event constant (``bge.events.LEFTMOUSE``).'''

RMB = events.RIGHTMOUSE
'''Right mouse button event constant (``bge.events.RIGHTMOUSE``).'''

MMB = events.MIDDLEMOUSE
'''Middle mouse button event constant (``bge.events.MIDDLEMOUSE``).'''

MOUSE_BUTTONS = {
    'LMB': LMB,
    'RMB': RMB,
    'MMB': MMB
}
'''Mapping from string names ``"LMB"``, ``"RMB"``, ``"MMB"`` to their ``bge.events`` constants.'''


def mouse_over(game_object: GameObject) -> bool:
    '''Return ``True`` if the mouse cursor is hovering over *game_object*.

    Casts a screen ray from the active camera using the current mouse position.

    :param game_object: The :class:`~bge.types.KX_GameObject` to test.
    :returns: ``True`` when the ray target matches *game_object*.
    '''
    scene = game_object.scene
    camera = scene.active_camera
    distance = 2.0 * camera.getDistanceTo(game_object)
    mouse = logic.mouse
    mouse_position = mouse.position
    target = camera.getScreenRay(
        mouse_position[0],
        mouse_position[1],
        distance
    )
    return target is game_object


def set_mouse_position(x: int, y: int, absolute: bool = False) -> None:
    '''Move the mouse cursor to (*x*, *y*).

    :param x: Horizontal position. Normalised 0–1 unless *absolute* is ``True``.
    :param y: Vertical position. Normalised 0–1 unless *absolute* is ``True``.
    :param absolute: When ``True``, treat *x*/*y* as pixel coordinates.
    '''
    if absolute:
        render.setMousePosition(x, y)
        return
    render.setMousePosition(
        int(x * render.getWindowWidth()),
        int(y * render.getWindowHeight())
    )


def get_mouse_position(absolute: bool = False) -> Vector:
    '''Return the current mouse cursor position.

    :param absolute: When ``True``, return pixel coordinates; otherwise return
        normalised 0–1 values.
    :returns: :class:`mathutils.Vector` of ``(x, y)``.
    '''
    pos = logic.mouse.position
    if absolute:
        return Vector((
            int(pos[0] * render.getWindowWidth()),
            int(pos[1] * render.getWindowHeight())
        ))
    return Vector(pos)


def mouse_moved(tap: bool = False) -> bool:
    '''Return ``True`` when the mouse cursor has moved.

    :param tap: When ``True``, return ``True`` only on the first consecutive
        frame of movement (activation frame only).
    :returns: ``True`` if the mouse is moving (or was activated this frame).
    '''
    if tap:
        return (
            MOUSE_EVENTS[events.MOUSEX].activated or
            MOUSE_EVENTS[events.MOUSEY].activated
        )
    else:
        return (
            MOUSE_EVENTS[events.MOUSEX].active or
            MOUSE_EVENTS[events.MOUSEY].active or
            MOUSE_EVENTS[events.MOUSEX].activated or
            MOUSE_EVENTS[events.MOUSEY].activated
        )


def mouse_tap(button=events.LEFTMOUSE) -> bool:
    '''Return ``True`` on the single frame a mouse button is first pressed.

    :param button: Button constant — use :data:`LMB`, :data:`RMB`, or
        :data:`MMB` from :mod:`uplogic.input`, or the string ``"LMB"``,
        ``"RMB"``, ``"MMB"``.
    :returns: ``True`` on the activation frame.
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].activated or
        MOUSE_EVENTS[button].activated
    )


def mouse_down(button=events.LEFTMOUSE) -> bool:
    '''Return ``True`` while a mouse button is held down (including the first frame).

    :param button: Button constant or string name (``"LMB"``, ``"RMB"``, ``"MMB"``).
    :returns: ``True`` while the button is active or activated.
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].active or
        MOUSE_EVENTS[button].activated or
        MOUSE_EVENTS[button].active or
        MOUSE_EVENTS[button].activated
    )


def mouse_press(button=events.LEFTMOUSE, down=False) -> bool:
    '''Return ``True`` when a mouse button is tapped, or (when *down* is ``True``) also
    while it is held.

    :param button: Button constant or string name (``"LMB"``, ``"RMB"``, ``"MMB"``).
    :param down: When ``True``, also return ``True`` while the button is held.
    :returns: ``True`` on activation, or while active when *down* is ``True``.
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].active or
        MOUSE_EVENTS[button].activated or
        MOUSE_EVENTS[button].active or
        MOUSE_EVENTS[button].activated
    ) if down else (
        MOUSE_EVENTS[button].activated or
        MOUSE_EVENTS[button].activated
    )


def mouse_up(button=events.LEFTMOUSE) -> bool:
    '''Return ``True`` on the single frame a mouse button is released.

    :param button: Button constant or string name (``"LMB"``, ``"RMB"``, ``"MMB"``).
    :returns: ``True`` on the release frame.
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].released
    )


_buttons_active = {}


def mouse_pulse(button=events.LEFTMOUSE, time: float = .4) -> bool:
    '''Return ``True`` on the first press and again once the button has been held
    for more than *time* seconds (useful for auto-repeat).

    :param button: Button constant or string name (``"LMB"``, ``"RMB"``, ``"MMB"``).
    :param time: Hold duration in seconds before continuous activation begins.
    :returns: ``True`` on the tap frame or while held past *time*.
    '''
    button = MOUSE_BUTTONS.get(button, button)
    evt = MOUSE_EVENTS[button]
    if evt.activated:
        _buttons_active[button] = 0
        return True
    k = _buttons_active.get(button, 0)
    _buttons_active[button] = k + (1 / (logic.getAverageFrameRate() or 0.01))
    if _buttons_active[button] > time:
        return evt.active
    return False


def mouse_wheel(tap: bool = False) -> int:
    '''Return the mouse wheel direction this frame.

    :param tap: When ``True``, only return a non-zero value on the activation
        frame; otherwise return non-zero while the wheel is scrolling.
    :returns: ``1`` if scrolled up, ``-1`` if scrolled down, ``0`` if idle.
    '''
    if tap:
        return (
            MOUSE_EVENTS[events.WHEELUPMOUSE].activated -
            MOUSE_EVENTS[events.WHEELDOWNMOUSE].activated
        )
    else:
        return (
            (
                MOUSE_EVENTS[events.WHEELUPMOUSE].activated or
                MOUSE_EVENTS[events.WHEELUPMOUSE].active
            ) - (
                MOUSE_EVENTS[events.WHEELDOWNMOUSE].activated or
                MOUSE_EVENTS[events.WHEELDOWNMOUSE].active
            )
        )


class Mouse():
    '''Stateful mouse wrapper that tracks cursor position and frame-to-frame
    movement delta.

    Registers itself in the scene ``pre_draw`` list when :attr:`enabled` is
    ``True`` (the default).
    '''

    _deprecated = False

    def __init__(self) -> None:
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULMouse class will be renamed to "Mouse" in future releases!')
        self._position = get_mouse_position()
        '''Staggered updated mouse position for pos difference calculation.'''
        self.movement = (0, 0)
        '''Movement of the mouse as a tuple ``(x, y)``.'''
        self.enabled = True

    @property
    def enabled(self):
        '''Whether the per-frame position-tracking update is active. Setting to ``False`` removes the update from the scene pre-draw list.'''
        return self.update in logic.getCurrentScene().pre_draw

    @enabled.setter
    def enabled(self, val):
        pre_draw = logic.getCurrentScene().pre_draw
        if val and self.update not in pre_draw:
            pre_draw.append(self.update)
        elif not val and self.update in pre_draw:
            pre_draw.remove(self.update)

    @property
    def position(self):
        '''Cursor position as a :class:`mathutils.Vector` of normalised ``(x, y)`` values in the range ``[0, 1]``. Setting this moves the cursor.'''
        return get_mouse_position()

    @position.setter
    def position(self, val):
        render.setMousePosition(
            int(val[0] * render.getWindowWidth()),
            int(val[1] * render.getWindowHeight())
        )
        self._position = get_mouse_position()

    @property
    def moved(self):
        '''``True`` if the cursor moved this frame (read-only).'''
        return mouse_moved()

    @moved.setter
    def moved(self, val):
        console.debug('Mouse.moved is read-only!')

    @property
    def wheel(self):
        '''Mouse wheel direction this frame: ``1`` up, ``-1`` down, ``0`` idle (read-only).'''
        return mouse_wheel()

    @wheel.setter
    def wheel(self, val):
        console.debug('Mouse.wheel is read-only!')

    def update(self) -> None:
        '''Per-frame update: compute the cursor movement delta and store it in :attr:`movement`. Called automatically via the scene pre-draw list.'''
        old_pos = self._position
        new_pos = self.position
        self.movement = (
            new_pos[0] - old_pos[0],
            new_pos[1] - old_pos[1]
        )
        self._position = new_pos

    def button_down(self, button: str = 'LMB'):
        '''Return ``True`` while *button* is held down.

        :param button: ``"LMB"``, ``"MMB"``, or ``"RMB"``.
        :returns: ``True`` while the button is active.
        '''
        return mouse_down(MOUSE_BUTTONS[button])

    def button_up(self, button: str = 'LMB'):
        '''Return ``True`` on the single frame *button* is released.

        :param button: ``"LMB"``, ``"MMB"``, or ``"RMB"``.
        :returns: ``True`` on the release frame.
        '''
        return mouse_up(MOUSE_BUTTONS[button])

    def button_tap(self, button: str = 'LMB'):
        '''Return ``True`` on the single frame *button* is first pressed.

        :param button: ``"LMB"``, ``"MMB"``, or ``"RMB"``.
        :returns: ``True`` on the activation frame.
        '''
        return mouse_tap(MOUSE_BUTTONS[button])


class ULMouse(Mouse):
    '''[DEPRECATED] Use :class:`Mouse` instead.'''
    _deprecated = True


MOUSE = Mouse()


class MouseLook():
    '''Mouse-driven first-person look controller.

    Translates mouse cursor movement into rotations applied to a body object
    (Z axis) and an optional head object (X/Y axis).  The controller can be
    toggled at any time via :attr:`enabled`.

    :param obj: Primary object to rotate around the Z axis.
    :param head: Secondary object for vertical rotation; defaults to *obj*.
    :param sensitivity: Mouse movement to rotation scale factor.
    :param use_cap_x: Enable rotation clamping on the Z axis.
    :param cap_x: ``(min, max)`` Z-axis rotation limits in degrees.
    :param use_cap_y: Enable rotation clamping on the X/Y axis.
    :param cap_y: ``(min, max)`` X/Y-axis rotation limits in degrees.
    :param invert: ``(invert_x, invert_y)`` flags for each axis.
    :param smoothing: Movement smoothing factor in ``[0, 1)``.
    :param local: When ``True``, apply rotations in local space.
    :param front: Front axis index (``1`` = Y, ``0`` = X; Blender default is ``1``).
    :param center_mouse: When ``True``, keep the cursor locked to screen centre.
    :param enabled: Whether to start the component active.
    '''

    _deprecated = False

    def __init__(
        self,
        obj: GameObject,
        head: GameObject = None,
        sensitivity: float = 1.0,
        use_cap_x: bool = False,
        cap_x: tuple = (0, 0),
        use_cap_y: bool = False,
        cap_y: tuple = (-89, 89),
        invert: tuple = (False, False),
        smoothing: float = 0.0,
        local: bool = True,
        front: int = 1,
        center_mouse: bool = True,
        enabled: bool = True,
    ) -> None:
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULMouseLook class will be renamed to "MouseLook" in future releases!')
        self.obj = obj
        self.head = head if head else obj
        self._defaults = [
            obj.localOrientation.copy(),
            head.localOrientation.copy()
            if head else
            obj.localOrientation.copy()
        ]
        self.center_mouse = center_mouse
        self._old_mouse_pos = logic.mouse.position
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
        self.local = local
        self.axis_lock = [False, False]
        self.reset_factor = 0
        self.enabled = enabled
        self.get_data()
        self._active = True
        if enabled:
            self.mouse.position = self.screen_center

    @property
    def active(self):
        '''Whether the look controller is currently processing mouse input. Setting to ``False`` freezes rotation without stopping the update loop.'''
        return self._active

    @active.setter
    def active(self, val):
        if val and self._active is False:
            self.screen_center = (logic.mouse.position[0], logic.mouse.position[1])
            self.center = Vector(self.screen_center)
        self._active = bool(val)

    @property
    def enabled(self):
        '''Whether the per-frame update is registered. Setting to ``False`` also resets :attr:`initialized`.'''
        return self.update in logic.getCurrentScene().pre_draw

    @enabled.setter
    def enabled(self, val):
        pre_draw = logic.getCurrentScene().pre_draw
        if val and self.update not in pre_draw:
            pre_draw.append(self.update)
        elif not val and self.update in pre_draw:
            self.initialized = False
            pre_draw.remove(self.update)

    @property
    def rotation(self):
        '''Tuple of ``(body_world_orientation, head_world_orientation)``. Setting writes both orientations simultaneously.'''
        return self.obj.worldOrientation, self.head.worldOrientation

    @rotation.setter
    def rotation(self, val):
        self.obj.worldOrientation = val[0]
        self.head.worldOrientation = val[1]

    def stop(self, reset: bool = False):
        '''Stop the controller and optionally reset both objects to their original orientations.

        :param reset: When ``True``, call :meth:`reset` before stopping.
        '''
        self.enabled = False
        if reset:
            self.reset()
        self.initialized = False

    def disable(self):
        '''Deactivate the controller (alias for setting :attr:`enabled` to ``False``).'''
        self.enabled = False

    def enable(self):
        '''Activate the controller (alias for setting :attr:`enabled` to ``True``).'''
        self.enabled = True

    @property
    def movement(self):
        return Vector((self._x, self._y))

    def reset(self, factor=1):
        '''Restore both objects to their original orientations captured at construction.

        :param factor: When ``< 1``, lerp towards the default orientation each
            frame using :func:`~uplogic.events.schedule_callback` for a smooth
            reset; when ``1``, snap immediately.
        '''
        if factor < 1:
            self.enabled = False
            if self.reset_factor < 1:
                self.obj.localOrientation = self.obj.localOrientation.lerp(self._defaults[0], factor)
                self.head.localOrientation = self.head.localOrientation.lerp(self._defaults[1], factor)
                self.reset_factor = interpolate(self.reset_factor, 1, factor, threshold=.0)
                # schedule_callback(self.reset, arg=factor)
            else:
                self.reset_factor = 0
                self.reset()
        else:
            self.obj.localOrientation = self._defaults[0]
            self.head.localOrientation = self._defaults[1]

    def get_data(self):
        '''Initialise screen-centre coordinates from the current window dimensions. Not intended for manual use.'''
        self.mouse = logic.mouse
        if self.center_mouse:
            self.x = render.getWindowWidth()//2
            self.y = render.getWindowHeight()//2
            self.screen_center = (
                self.x / render.getWindowWidth(),
                self.y / render.getWindowHeight()
            )
        else:
            self.screen_center = self._old_mouse_pos
        self.center = Vector(self.screen_center)

    def update(self):
        '''Per-frame update: compute the mouse offset, apply smoothing, enforce caps, and rotate both objects. Called automatically via the scene pre-draw list.'''
        # self.get_data()
        if not self.initialized and self.center_mouse:
            self.mouse.position = self.screen_center
            self.initialized = True
            return
        game_object_x = self.obj
        game_object_y = self.head
        sensitivity = self.sensitivity * 10
        cap_x = self.cap_x
        cap_y = self.cap_y
        invert = self.invert
        smooth = 1 - (self.smoothing * .99)

        mouse_position = Vector(self.mouse.position) if self.active else self.center
        offset = (mouse_position - self.center) * -0.2

        if invert[1] is True:
            offset.y = -offset.y
        if invert[0] is True:
            offset.x = -offset.x
        offset *= sensitivity * .001

        self._x = offset.x = interpolate(self._x, offset.x * render.getWindowWidth(), smooth, 0)
        self._y = offset.y = interpolate(self._y, offset.y * render.getWindowHeight(), smooth, 0)

        if self.use_cap_x:
            lowercapX = cap_x[0] * pi / 180
            uppercapX = cap_x[1] * pi / 180
            objectRotation = game_object_x.localOrientation.to_euler()

            if objectRotation.z + offset.x > uppercapX:
                offset.x = 0
                objectRotation.z = uppercapX
                game_object_x.localOrientation = objectRotation

            if objectRotation.z + offset.x < lowercapX:
                offset.x = 0
                objectRotation.z = lowercapX
                game_object_x.localOrientation = objectRotation

        if not self.axis_lock[0]:
            game_object_x.applyRotation((0, 0, offset.x), self.local)

        rot_axis = 1 - self.front
        if self.use_cap_y:
            lowercapY = cap_y[0] * pi / 180
            uppercapY = cap_y[1] * pi / 180
            objectRotation = game_object_y.localOrientation.to_euler()

            if objectRotation[rot_axis] + offset.y > uppercapY:
                objectRotation[rot_axis] = uppercapY
                game_object_y.localOrientation = objectRotation
                offset.y = 0

            if objectRotation[rot_axis] + offset.y < lowercapY:
                objectRotation[rot_axis] = lowercapY
                game_object_y.localOrientation = objectRotation
                offset.y = 0

        rot = [0, 0, 0]
        rot[1-self.front] = offset.y
        if not self.axis_lock[1]:
            game_object_y.applyRotation((*rot, ), True)
        if self.center_mouse and self.active and (Vector(self.mouse.position) - Vector(self.screen_center)).length > .00001:
            self.mouse.position = self.screen_center
            self._old_mouse_pos = self.mouse.position
        elif not self.center_mouse:
            mpos = list(self.mouse.position)
            opos = self._old_mouse_pos
            xpos = mpos[0] if 0 <= mpos[0] <= 1 else opos[0]
            ypos = mpos[1] if 0 <= mpos[1] <= 1 else opos[1]
            self._old_mouse_pos = (xpos, ypos)
            threshold = 0.001
            mpos[0] = clamp(mpos[0], threshold, 1-threshold)
            mpos[1] = clamp(mpos[1], threshold, 1-threshold)
            self.mouse.position = (mpos[0], mpos[1])


class ULMouseLook(MouseLook):
    '''[DEPRECATED] Use :class:`MouseLook` instead.'''
    _deprecated = True

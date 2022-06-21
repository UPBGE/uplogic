from math import pi
from bge import logic
from bge import events
from bge import render
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.utils import interpolate
from uplogic.events import schedule_callback


MOUSE_EVENTS = logic.mouse.inputs
'''Reference to `bge.logic.mouse.inputs`
'''

LMB = events.LEFTMOUSE
RMB = events.RIGHTMOUSE
MMB = events.MIDDLEMOUSE

MOUSE_BUTTONS = {
    'LMB': LMB,
    'RMB': RMB,
    'MMB': MMB
}


def set_mouse_position(x: int, y: int, absolute: bool = False) -> None:
    if absolute:
        render.setMousePosition(x, y)
        return
    render.setMousePosition(
        int(x * render.getWindowWidth()),
        int(y * render.getWindowHeight())
    )


def get_mouse_position(absolute: bool = False) -> tuple:
    pos = logic.mouse.position
    if absolute:
        return (
            int(pos[0] * render.getWindowWidth()),
            int(pos[1] * render.getWindowHeight())
        )
    return pos


def mouse_moved(tap: bool = False) -> bool:
    '''Detect mouse movement.

    :param tap: Only use the first consecutive `True` output

    :returns: boolean
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
    '''Detect mouse button tap.

    :param button: can be either `LMB`, `RMB` or `MMB` from `uplogic.input`

    :returns: boolean
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].activated or
        MOUSE_EVENTS[button].activated
    )


def mouse_down(button=events.LEFTMOUSE) -> bool:
    '''Detect mouse button held down.

    :param button: can be either `LMB`, `RMB` or `MMB` from `uplogic.input`

    :returns: boolean
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].active or
        MOUSE_EVENTS[button].activated or
        MOUSE_EVENTS[button].active or
        MOUSE_EVENTS[button].activated
    )


def mouse_up(button=events.LEFTMOUSE) -> bool:
    '''Detect mouse button released.

    :param button: can be either `LMB`, `RMB` or `MMB` from `uplogic.input`

    :returns: boolean
    '''
    button = MOUSE_BUTTONS.get(button, button)
    return (
        MOUSE_EVENTS[button].released
    )


def mouse_wheel(tap: bool = False) -> int:
    '''Detect mouse wheel activity.

    :param tap: Only use the first consecutive `True` output

    :returns: -1 if wheel down, 0 if idle, 1 if wheel up
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


class ULMouse():
    """Mouse Wrapper for accessing mouse data."""
    def __init__(self) -> None:
        self._position = get_mouse_position()
        """Staggered updated mouse position for pos difference calculation."""
        self.movement = (0, 0)
        """Movement of the mouse as a tuple `(x, y)`."""
        self.active = True

    @property
    def active(self):
        """Tracking state of this component."""
        return self.update in logic.getCurrentScene().pre_draw

    @active.setter
    def active(self, val):
        pre_draw = logic.getCurrentScene().pre_draw
        if val and self.update not in pre_draw:
            pre_draw.append(self.update)
        elif not val and self.update in pre_draw:
            pre_draw.remove(self.update)

    @property
    def position(self):
        """Position of the mouse as a tuple of `(x, y)` ranging from 0-1 on both
        axis."""
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
        """`True` if the mouse is moved, `False` if idle."""
        return mouse_moved()

    @moved.setter
    def moved(self, val):
        print('ULMouse.moved is read-only!')

    @property
    def wheel(self):
        """Mouse wheel difference.
        
        -1 if scolled down, 0 if idle, 1 if scrolled up."""
        return mouse_wheel()

    @wheel.setter
    def wheel(self, val):
        print('ULMouse.wheel is read-only!')

    def update(self) -> None:
        """This is executed each frame if component is active."""
        old_pos = self._position
        new_pos = self.position
        self.movement = (
            new_pos[0] - old_pos[0],
            new_pos[1] - old_pos[1]
        )
        self._position = new_pos

    def button_down(self, button: str = 'LMB'):
        """Check if a button on the mouse is held down.
        
        :param `button`: The button to check for; `str` of [`'LMB'`, `'MMB'`,
        `'RMB'`]"""
        return mouse_down(MOUSE_BUTTONS[button])

    def button_up(self, button: str = 'LMB'):
        """Check if a button on the mouse is released.
        
        :param `button`: The button to check for; `str` of [`'LMB'`, `'MMB'`,
        `'RMB'`]"""
        return mouse_up(MOUSE_BUTTONS[button])

    def button_tap(self, button: str = 'LMB'):
        """Check if a button on the mouse is pressed once.
        
        :param `button`: The button to check for; `str` of [`'LMB'`, `'MMB'`,
        `'RMB'`]"""
        return mouse_tap(MOUSE_BUTTONS[button])


class ULMouseLook():
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
        sensitivity: float = 1.0,
        use_cap_x: bool = False,
        cap_x: tuple = (0, 0),
        use_cap_y: bool = False,
        cap_y: tuple = (-89, 89),
        invert: tuple = (False, True),
        smoothing: float = 0.0,
        local: bool = True,
        front: int = 1,
        active: bool = True
    ) -> None:
        self.obj = obj
        self.head = head if head else obj
        self._defaults = [
            obj.localOrientation.copy(),
            head.localOrientation.copy()
            if head else
            obj.localOrientation.copy()
        ]
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
        self.get_data()
        self.mouse.position = self.screen_center
        self.active = active

    @property
    def active(self):
        """State of this component."""
        return self.update in logic.getCurrentScene().pre_draw

    @active.setter
    def active(self, val):
        pre_draw = logic.getCurrentScene().pre_draw
        if val and self.update not in pre_draw:
            pre_draw.append(self.update)
        elif not val and self.update in pre_draw:
            self.initialized = False
            pre_draw.remove(self.update)

    @property
    def rotation(self):
        """Global body and head orientation."""
        return self.obj.worldOrientation, self.head.worldOrientation

    @rotation.setter
    def rotation(self, val):
        self.obj.worldOrientation = val[0]
        self.head.worldOrientation = val[1]

    def stop(self, reset: bool = False):
        """Stop this component.
        
        :param `reset`: Reset the orientation of objects to their original
        state."""
        self.active = False
        if reset:
            self.reset()
        self.initialized = False

    def disable(self):
        """Set this component to inactive."""
        self.active = False

    def enable(self):
        """Set this component to active."""
        self.active = True

    def reset(self, factor=1):
        """Reset the orientation of the objects in this component to their
        original state.
        
        :param `factor`: Smoothing factor of the reset. If < 1, component will
        be reset smoothly."""
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

    def get_data(self):
        """Get data for this component.
        
        Not intended for manual use."""
        self.x = render.getWindowWidth()//2
        self.y = render.getWindowHeight()//2
        self.screen_center = (
            self.x / render.getWindowWidth(),
            self.y / render.getWindowHeight()
        )
        self.center = Vector(self.screen_center)
        self.mouse = logic.mouse

    def update(self):
        """This is executed each frame if component is active."""
        self.get_data()
        if not self.initialized:
            self.mouse.position = self.screen_center
            self.initialized = True
            return
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

        mouse_position = Vector(self.mouse.position)
        offset = (mouse_position - self.center) * -0.2

        if invert[1] is False:
            offset.y = -offset.y
        if invert[0] is True:
            offset.x = -offset.x
        offset *= sensitivity

        self._x = offset.x = interpolate(self._x, offset.x, smooth, 0)
        self._y = offset.y = interpolate(self._y, offset.y, smooth, 0)

        if self.use_cap_x:
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
        if (Vector(self.mouse.position) - Vector(self.screen_center)).length > .00001:
        # if self.mouse.position != self.screen_center:
            self.mouse.position = self.screen_center
        self.done = True

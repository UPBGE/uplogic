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


class ULMouseData():
    def __init__(self) -> None:
        self.position = get_mouse_position()
        self.movement = (0, 0)
        self.wheel = mouse_wheel()
        logic.getCurrentScene().pre_draw.append(self.update)

    def update(self):
        old_pos = self.position
        new_pos = get_mouse_position()
        self.movement = (
            new_pos[0] - old_pos[0],
            new_pos[1] - old_pos[1]
        )
        self.position = new_pos
        self.wheel = mouse_wheel()

    def destroy(self):
        logic.getCurrentScene().pre_draw.remove(self.update)


def set_mouse_position(x: int, y: int, absolute: bool = False):
    if absolute:
        render.setMousePosition(x, y)
        return
    render.setMousePosition(
        int(x * render.getWindowWidth()),
        int(y * render.getWindowHeight())
    )


def get_mouse_position(absolute: bool = False):
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


class ULMouseLook():

    def __init__(
        self,
        obj: GameObject,
        head=None,
        sensitivity=1.0,
        use_cap_x=False,
        cap_x=[0, 0],
        use_cap_y=False,
        cap_y=[-89, 89],
        invert=[False, True],
        smoothing=0.0,
        local=False,
        front=1,
        active=True
    ) -> None:
        self.obj = obj
        self.head = head if head else obj
        self._defaults = [obj.localOrientation.copy(), head.localOrientation.copy()]
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
        self.get_data()
        self.mouse.position = self.screen_center
        self.active = active

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, val):
        scene = logic.getCurrentScene()
        if val and self.update not in scene.pre_draw:
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

    def get_data(self):
        self.x = render.getWindowWidth()//2
        self.y = render.getWindowHeight()//2
        self.screen_center = (
            self.x / render.getWindowWidth(),
            self.y / render.getWindowHeight()
        )
        self.center = Vector(self.screen_center)
        self.mouse = logic.mouse

    def update(self):
        self.get_data()
        if not self.initialized:
            self.mouse.position = self.screen_center
            self.initialized = True
            return
        game_object_x = self.obj
        game_object_y = self.head
        sensitivity = self.sensitivity * 10
        use_cap_x = self.use_cap_x
        use_cap_y = self.use_cap_y
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

        if use_cap_x:
            objectRotation = game_object_x.localOrientation.to_euler()

            if objectRotation.z + offset.x > uppercapX:
                offset.x = 0
                objectRotation.z = uppercapX
                game_object_x.localOrientation = objectRotation.to_matrix()

            if objectRotation.z + offset.x < lowercapX:
                offset.x = 0
                objectRotation.z = lowercapX
                game_object_x.localOrientation = objectRotation.to_matrix()

        game_object_x.applyRotation((0, 0, offset.x), self.local)

        rot_axis = 1 - self.front
        if use_cap_y:
            objectRotation = game_object_y.localOrientation.to_euler()

            if objectRotation[rot_axis] + offset.y > uppercapY:
                objectRotation[rot_axis] = uppercapY
                game_object_y.localOrientation = objectRotation.to_matrix()
                offset.y = 0

            if objectRotation[rot_axis] + offset.y < lowercapY:
                objectRotation[rot_axis] = lowercapY
                game_object_y.localOrientation = objectRotation.to_matrix()
                offset.y = 0

        rot = [0, 0, 0]
        rot[1-self.front] = offset.y
        game_object_y.applyRotation((*rot, ), True)
        if (Vector(self.mouse.position) - Vector(self.screen_center)).length > .00001:
        # if self.mouse.position != self.screen_center:
            self.mouse.position = self.screen_center
        self.done = True

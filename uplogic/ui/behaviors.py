from bge import render
from uplogic.input import MOUSE
from uplogic.input.mouse import MOUSE_EVENTS, LMB, RMB
from mathutils import Vector
from uplogic.utils.math import rotate2d


class HoverBehavior():
    @property
    def hover(self):
        if not self.active:
            return False
        screen_size = [render.getWindowWidth(), render.getWindowHeight()]
        mpos = Vector((MOUSE.position.x * screen_size[0], (1 - MOUSE.position.y) * screen_size[1]))
        mpos = rotate2d(mpos, self.pivot, -self._draw_angle)
        dsize = self._draw_size
        is_hover = (
            self.pos_abs[0] <= mpos.x <= self.pos_abs[0] + dsize[0] and
            self.pos_abs[1] <= mpos.y <= self.pos_abs[1] + dsize[1] and
            not self.canvas._hover_consumed
        )
        return is_hover


class MouseListener():
    """Mixin class for widgets that need mouse input.

    You will need to call `MouseListener.evaluate(self)` to update the behavior state.\n
    This data is independent of hovering, it just gives generic mouse button information.
    """

    def evaluate(self):
        self.clicked = False
        self.released = False
        self.hold = False
        if MOUSE_EVENTS[LMB].active and not self._down:
            self.on_click(self)
            self.on_press(self)
            self._down = True
            self.clicked = True
        elif not MOUSE_EVENTS[LMB].active and self._down:
            self.on_release(self)
            self._down = False
            self.released = True
        elif self._down:
            self.hold = True
            self.on_hold(self)

    def on_click(self, widget):
        pass

    def on_press(self, widget):
        pass

    def on_release(self, widget):
        pass

    def on_hold(self, widget):
        pass

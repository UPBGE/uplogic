from bge import render
from uplogic.input import MOUSE
from uplogic.input.mouse import MOUSE_EVENTS, LMB, RMB
from mathutils import Vector
from uplogic.utils.math import rotate2d


class HoverBehavior():
    '''Mixin that adds pixel-accurate hover detection to a widget.

    Converts the normalised mouse position to pixel space, corrects for the
    widget's accumulated rotation, and checks against ``pos_pixel`` /
    ``size_pixel``.  The result is ``False`` if the canvas has already
    consumed the hover event for this frame.
    '''

    @property
    def hover(self):
        '''``True`` when the cursor is inside this widget's pixel bounds and no
        other widget has already consumed the hover event this frame.
        '''
        if not self.active:
            return False
        screen_size = [render.getWindowWidth(), render.getWindowHeight()]
        mpos = Vector((MOUSE.position.x * screen_size[0], (1-MOUSE.position.y) * screen_size[1]))
        mpos = rotate2d(mpos, self.pivot, -self._draw_angle)
        pxsize = self.size_pixel
        pxpos = self.pos_pixel
        consumed = self.canvas._hover_consumed if self.canvas is not None else True
        is_hover = (
            pxpos[0] <= mpos.x <= pxpos[0] + pxsize[0] and
            pxpos[1] <= mpos.y <= pxpos[1] + pxsize[1] and
            not consumed
        )
        return is_hover


class MouseListener():
    '''Mixin class for widgets that need global mouse input.

    Call ``MouseListener.evaluate(self)`` each frame to update the state
    flags.  Unlike :class:`HoverBehavior`, this mixin reacts to LMB events
    regardless of cursor position.

    State flags reset to ``False`` at the start of each :meth:`evaluate`
    call:

    - ``clicked`` — ``True`` for one frame on initial LMB press
    - ``released`` — ``True`` for one frame when LMB is released
    - ``hold`` — ``True`` while LMB is held after the initial press
    '''

    def evaluate(self):
        '''Update click/release/hold state flags and fire event callbacks.

        Must be called manually each frame (e.g. from the widget's own
        ``evaluate`` override).
        '''
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
        '''Override to react to an initial LMB press.'''
        pass

    def on_press(self, widget):
        '''Override to react to an LMB press (fired on the same frame as :meth:`on_click`).'''
        pass

    def on_release(self, widget):
        '''Override to react to LMB release.'''
        pass

    def on_hold(self, widget):
        '''Override to react to a held LMB (fired every frame while held).'''
        pass

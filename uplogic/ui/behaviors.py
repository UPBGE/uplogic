from bge import render
from uplogic.input import MOUSE
from mathutils import Vector


class HoverBehavior():
    @property
    def hover(self):
        screen_size = [render.getWindowWidth(), render.getWindowHeight()]
        mpos = Vector((MOUSE.position.x, 1 - MOUSE.position.y))
        dsize = self._draw_size
        return (
            self.pos_abs[0] <= mpos.x * screen_size[0] <= self.pos_abs[0] + dsize[0] and
            self.pos_abs[1] <= mpos.y * screen_size[1] <= self.pos_abs[1] + dsize[1] and
            not self.canvas._hover_consumed
        )

from bge import render
from uplogic.input import MOUSE
from mathutils import Vector


class HoverBehavior():
    @property
    def hover(self):
        screen_size = [render.getWindowWidth(), render.getWindowHeight()]
        mpos = Vector((MOUSE.position.x, 1 - MOUSE.position.y))
        return (
            self.pos_abs[0] <= mpos.x * screen_size[0] <= self.pos_abs[0] + self.size[0] and
            self.pos_abs[1] <= mpos.y * screen_size[1] <= self.pos_abs[1] + self.size[1] and
            not self.system._mouse_consumed
        )

from .widget import Widget
from bge import render
import gpu
import bge


class Canvas(Widget):
    """The base class for UI layouts. This class has no visual representation
    and spans the whole screen. It is intended to manage collections of widgets
    more easily.

    A canvas cannot be attached to another widget and has its own update cycle.
    """

    def __init__(self):
        super().__init__((0, 0), (0, 0))
        self._hover_consumed = False
        self._click_consumed = False
        self.use_clipping = False
        self._to_evaluate: list[Widget] = []
        bge.logic.getCurrentScene().post_draw.append(self.draw)

    @property
    def _draw_pos(self):
        return [0, 0]

    @property
    def pivot(self):
        return (0, 0)

    @property
    def _draw_size(self):
        return [
            render.getWindowWidth(),
            render.getWindowHeight()
        ]

    @property
    def clipping(self):
        return [
            0,
            render.getWindowWidth(),
            render.getWindowHeight(),
            0
        ]

    @property
    def parent(self):
        return None

    @parent.setter
    def parent(self, val):
        self._parent = None
        # self._parent = val
        # self.pos = self.pos

    def draw(self):
        if not self.show:
            return
        gpu.state.blend_set('ALPHA')
        super().draw()
        self._hover_consumed = False
        for w in self._to_evaluate.__reversed__():
            w._evaluate()
        while self._to_evaluate:
            self._to_evaluate.pop().update()

    def update(self):
        pass

from .widget import Widget
from uplogic.shaders.buffer import Buffer
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
        self._old_width = bge.render.getWindowWidth()
        self._old_height = bge.render.getWindowHeight()
        self.image = Buffer()
        self.use_clipping = False
        self._to_evaluate: list[Widget] = []
        bge.logic.getCurrentScene().post_draw.append(self.draw)

    def remove(self):
        while self.draw in bge.logic.getCurrentScene().post_draw:
            bge.logic.getCurrentScene().post_draw.remove(self.draw)

    def fetch_size(self):
        for c in self.children:
            c.size = c.size
            c.pos = c.pos
            c.parent = c.parent

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

    def set_uniforms(self):
        pass

    def draw(self):
        width = bge.render.getWindowWidth()
        height = bge.render.getWindowHeight()
        if width != self._old_width or height != self._old_height:
            self.fetch_size()
        self._old_width = width
        self._old_height = height
        if not self.show:
            return
        gpu.state.blend_set('ALPHA')
        super().draw()
        self._hover_consumed = False
        for w in self._to_evaluate.__reversed__():
            w.evaluate()
        while self._to_evaluate:
            self._to_evaluate.pop().update()

    def update(self):
        pass

    def new_layer(self):
        layer = Layer()
        self.add_widget(layer)
        return layer


class Layer(Widget):

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
        """The widget whose position and size to use relatively."""
        return self._parent

    @parent.setter
    def parent(self, val):
        if not isinstance(val, Canvas):
            raise TypeError('ui.Layout can only be added to ui.Canvas type!')
        if self.parent is not val and self.parent:
            self.parent.remove_widget(self)
        if self.use_clipping is None:
            self.use_clipping = val.use_clipping
        self._parent = val
        self.pos = self.pos
        self.size = self.size
        for c in self.children:
            c.parent = c.parent
        self._build_shader()

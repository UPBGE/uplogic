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

    _is_canvas = True

    def __init__(self, show=True):
        super().__init__((0, 0), (0, 0), show=show)
        self._hover_consumed = False
        self._click_consumed = False
        self._old_width = bge.render.getWindowWidth()
        self._old_height = bge.render.getWindowHeight()
        self.use_clipping = False
        self._to_evaluate: list[Widget] = []
        self.register()
        self.start()
    
    def register(self):
        bge.logic.getCurrentScene().post_draw.insert(0, self.draw)

    def unregister(self):
        while self.draw in bge.logic.getCurrentScene().post_draw:
            bge.logic.getCurrentScene().post_draw.remove(self.draw)

    def remove(self):
        self.unregister()

    def fetch_size(self):
        for c in self.children:
            c.size = c.size
            c.pos = c.pos
            c.parent = c.parent

    @property
    def size_pixel(self):
        return [
            render.getWindowWidth(),
            render.getWindowHeight()
        ]

    @property
    def width_pixel(self):
        return render.getWindowWidth()

    @property
    def height_pixel(self):
        return render.getWindowHeight()

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
        self._click_consumed = False
        for w in self._to_evaluate.__reversed__():
            if w.parent:
                w.evaluate()
        self.update()
        while self._to_evaluate:
            w = self._to_evaluate.pop()
            if w.parent:
                w.update()
        

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
            raise TypeError('ui.Layer can only be added to ui.Canvas type!')
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

from .widget import Widget
import gpu
from bge import render


class Layout(Widget):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 100.],
        color=(0, 0, 0, 0),
        relative={},
        border_width=1,
        border_color=(0, 0, 0, 0),
        halign='left',
        valign='bottom'
    ):
        super().__init__(pos, size, color, relative, halign=halign, valign=valign)
        self.border_width = border_width
        self.border_color = border_color

    @property
    def opacity(self):
        return self.color[3]

    @opacity.setter
    def opacity(self, val):
        self.color[3] = val
        self.border_color[3] = val

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color):
        self._border_color = list(color)

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, val):
        self._border_width = int(val)

    def draw(self):
        gpu.state.line_width_set(self.border_width)
        gpu.state.point_size_set(self.border_width)
        self.shader.uniform_float("color", self.color)
        self.batch.draw(self.shader)
        self.shader.uniform_float("color", self.border_color)
        self.batch_line.draw(self.shader)
        self.batch_points.draw(self.shader)
        super().draw()


class RelativeLayout(Layout):
    @property
    def clipping(self):
        return [
            0,
            render.getWindowWidth(),
            render.getWindowHeight(),
            0
        ]


class FloatLayout(Layout):

    @property
    def pos_abs(self):
        return [0, 0]


class BoxLayout(Layout):
    def __init__(
            self,
            orientation='vertical',
            pos=[0, 0],
            size=[100, 100],
            color=(0, 0, 0, 0),
            relative={},
            border_width=1,
            border_color=(0, 0, 0, 0),
            spacing=0,
            halign='left',
            valign='bottom'
        ):
        self.orientation = orientation
        self.spacing = spacing
        super().__init__(pos, size, color, relative, border_width, border_color, halign=halign, valign=valign)
        self.use_clipping = True

    def add_widget(self, widget):
        super().add_widget(widget)
        self.arrange()
    
    def remove_widget(self, widget):
        super().remove_widget(widget)
        self.arrange()

    def arrange(self):
        dsize = self._draw_size
        if self.orientation == 'horizontal':
            offset = 0
            for widget in self.children:
                widget.relative['pos'] = False
                widget.pos = [offset, dsize[1] - widget._draw_size[1]]
                offset += widget._draw_size[0] + self.spacing
        if self.orientation == 'vertical':
            offset = dsize[1]
            for widget in self.children:
                offset -= widget._draw_size[1]
                widget.relative['pos'] = False
                widget.pos = [0, offset]
                offset -= self.spacing

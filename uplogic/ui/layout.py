from .widget import Widget
import gpu
from bge import render


class Layout(Widget):

    def __init__(
        self,
        pos: list = [0., 0.],
        size: list = [100., 100.],
        bg_color: list = [0, 0, 0, 0],
        relative: dict = {},
        border_width: int = 1,
        border_color: list = [0, 0, 0, 0],
        halign: str = 'left',
        valign: str = 'bottom',
        angle=0
    ):
        self.border_width = border_width
        self.border_color = border_color
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle)

    @property
    def opacity(self):
        return self.bg_color[3]

    @opacity.setter
    def opacity(self, val):
        self.bg_color[3] = val
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
        super()._setup_draw()
        gpu.state.line_width_set(self.border_width)
        gpu.state.point_size_set(self.border_width)
        self._shader.uniform_float("color", self.bg_color)
        self._batch.draw(self._shader)
        self._shader.uniform_float("color", self.border_color)
        self._batch_line.draw(self._shader)
        self._batch_points.draw(self._shader)
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
            orientation: str = 'horizontal',
            pos: list = [0, 0],
            size: list = [100, 100],
            bg_color: list = (0, 0, 0, 0),
            relative: dict = {},
            border_width: int = 1,
            border_color: list = (0, 0, 0, 0),
            spacing: int = 0,
            halign: str = 'left',
            valign: str = 'bottom',
            angle=0
        ):
        self.orientation = orientation
        self.spacing = spacing
        super().__init__(pos, size, bg_color, relative, border_width, border_color, halign=halign, valign=valign, angle=angle)
        self.use_clipping = False

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        if self.parent is not val and self.parent:
            self.parent.remove_widget(self)
        if self.use_clipping is None:
            self.use_clipping = val.use_clipping
        self._parent = val
        self.pos = self.pos
        self.size = self.size
        self.arrange()

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


class GridLayout(BoxLayout):


    def __init__(
        self,
        orientation: str = 'vertical',
        pos: list = [0, 0],
        size: list = [100, 100],
        bg_color: list = [0, 0, 0, 0],
        relative: dict = {},
        border_width: int = 1,
        border_color: list = [0, 0, 0, 0],
        spacing: int = 0,
        cols: int = 2,
        rows: int = 2,
        halign: str = 'left',
        valign: str = 'bottom',
        angle=0
    ):
        super().__init__(
            orientation,
            pos,
            size,
            bg_color,
            relative,
            border_width,
            border_color,
            spacing,
            halign,
            valign,
            angle=angle
        )
        self.rows = rows
        self.cols = cols

    def add_widget(self, widget):
        max = self.rows * self.cols
        if len(self.children) < max:
            super().add_widget(widget)
            self.arrange()

    def arrange(self):
        dsize = self._draw_size
        idx = 0
        if self.orientation == 'horizontal':
            row = 0
            offset = 0
            for widget in self.children:
                offset_y = self._draw_size[1] / (self.rows) * row
                widget.relative['pos'] = False
                widget.pos = [offset, dsize[1] - widget._draw_size[1] - offset_y]
                offset += widget._draw_size[0] + self.spacing
                idx += 1
                if idx >= self.cols:
                    idx = 0
                    row += 1
                    offset = 0
        if self.orientation == 'vertical':
            col = 0
            offset = dsize[1]
            for widget in self.children:
                offset_x = self._draw_size[0] / (self.cols - 1) * col
                offset -= widget._draw_size[0]
                widget.relative['pos'] = False
                widget.pos = [offset_x, offset]
                offset -= self.spacing
                idx += 1
                if idx >= self.cols:
                    idx = 0
                    col += 1
                    offset = dsize[1]

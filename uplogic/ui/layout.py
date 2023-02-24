from .widget import Widget
import gpu


class Layout(Widget):

    def __init__(self, pos=[0., 0.], size=[100., 100.], relative={}, color=(0, 0, 0, 0), border_width=1.0, border_color=(0, 0, 0, 0)):
        super().__init__(pos, size, color, relative)
        self.border_width = border_width
        self.border_color = border_color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = list(color)

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color):
        self._border_color = list(color)

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
    pass


class FloatLayout(Layout):

    @property
    def pos_abs(self):
        return [0, 0]


class BoxLayout(Layout):
    def __init__(
            self,
            orientation='vertical',
            pos=[100, 100],
            size=[100, 100],
            color=(0, 0, 0, 0),
            border_width=1,
            border_color=(0, 0, 0, 0)
        ):
        super().__init__(pos, size, color, border_width, border_color)
    
    @property
    def offset(self):
        return (
            sum([widget.width for widget in self.children])
            if self.orientation == 'horizontal' else
            sum([widget.height for widget in self.children])
        )

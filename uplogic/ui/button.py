from .widget import Widget
from .behaviors import HoverBehavior
import gpu


class Button(Widget, HoverBehavior):

    def __init__(self, pos=[0., 0.], size=[100., 100.], relative={}, color=(0, 0, 0, 0), border_width=1.0, border_color=(0, 0, 0, 0), focus_color=(0, 0, 0, .5)):
        super().__init__(pos, size, color, relative)
        self.focus_color = focus_color
        self.border_width = border_width
        self.border_color = border_color
        self._in_focus = False

    def draw(self):
        gpu.state.line_width_set(self.border_width)
        gpu.state.point_size_set(self.border_width)
        self.shader.uniform_float("color", self.focus_color if self._in_focus else self.color)
        self.batch.draw(self.shader)
        self.shader.uniform_float("color", self.border_color)
        self.batch_line.draw(self.shader)
        self.batch_points.draw(self.shader)
        super().draw()

    def update(self):
        if self.hover:
            self._in_focus = True
            self.system._mouse_consumed = True
        else:
            self._in_focus = False
        super().update()


# class BoxLayout(Layout):

from uplogic.ui import Widget
from .behaviors import FocusBehavior
import gpu


class Button(Widget, FocusBehavior):

    def __init__(self, pos=[100., 100.], size=[100., 100.], color=(0, 0, 0, 0), border_width=1.0, border_color=(0, 0, 0, 0), focus_color=(0, 0, 0, .5)):
        super().__init__(pos, size)
        self.color = color
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

    def evaluate(self):
        if self.focus:
            self._in_focus = True
            self.system.mouse_consumed = True
        else:
            self._in_focus = False
        super().evaluate()


# class BoxLayout(Layout):

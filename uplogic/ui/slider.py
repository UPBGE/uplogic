from .widget import Widget
from .behaviors import HoverBehavior
from .button import Button
from .layout import RelativeLayout
from bge import render
import gpu
from uplogic.input.mouse import MOUSE_EVENTS, LMB, RMB, MOUSE
from uplogic.utils.math import clamp, map_range


class Slider(Widget):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 5.],
        relative={},
        halign='left',
        valign='bottom',
        orientation='horizontal',
        angle=0,
        bar_width=.3,
        bar_color=(1, 1, 1, 1),
        bar_hover_color=(1, 1, 1, 1),
        knob_size=1,
        knob_color=(.8, .8, .8, 1),
        knob_hover_color=(.8, .8, .8, 1),
        steps=-1,
        allow_bar_click=True
    ):
        super().__init__(pos, size, (0, 0, 0, 0), relative, halign=halign, valign=valign, angle=angle)
        self.border_width = 1
        self.border_color = (0, 0, 0, 1)
        self._horiz = orientation == 'horizontal'
        bar_size = (1, bar_width) if self._horiz else (bar_width, 1)
        self.bar = Button(pos=(.5, .5), size=bar_size, valign='center', halign='center', relative={'size': True, 'pos': True}, bg_color=bar_color, hover_color=bar_hover_color)
        self._slide_axis = 0 if self._horiz else 1
        self._up_axis = 1 if self._horiz else 0
        self.add_widget(self.bar)
        if allow_bar_click:
            self.bar.on_hold = self._on_press
        self.knob = Button(size=(0, 0), bg_color=knob_color, hover_color=knob_hover_color, valign='center', halign='center')
        self.knob_size = knob_size
        self.knob.on_hold = self._on_press
        self.add_widget(self.knob)
        self.steps = steps
        self.value = 0
        self._clicked = False
        self._released = False
        self._in_focus = False
        self._down = False

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
        self.value = self.value
        self.build_shader()

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        newval = value
        if self.steps > 0:
            newval -= newval % (1 / self.steps)
        self._value = clamp(newval)
        knob_size = self.knob._draw_size[self._slide_axis] * .5
        self.knob.pos[self._slide_axis] = map_range(self._value, 0, 1, knob_size, self._draw_size[self._slide_axis] - knob_size)
        size = self._draw_size
        self.knob.pos[self._up_axis] = (size[1]/2) if self._horiz else (size[0]/2)
        knob_width = (size[1] if self._horiz else size[0])
        self.knob.size = (knob_width * self.knob_size, knob_width * self.knob_size)

    def draw(self):
        super().draw()

    def _on_press(self, widget):
        pos = self._draw_pos
        knob_size = self.knob._draw_size[self._slide_axis] * .5
        self.value = map_range((MOUSE.position.x * render.getWindowWidth() if self._horiz else (1 - MOUSE.position.y) * render.getWindowHeight()), pos[self._slide_axis] + knob_size, pos[self._slide_axis] + self._draw_size[self._slide_axis] - knob_size, 0, 1)

    def on_hold(self, widget):
        pass

    def on_release(self, widget):
        pass

    def on_hover(self, widget):
        pass

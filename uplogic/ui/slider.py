from .widget import Widget
from .button import Button
from .layout import RelativeLayout
from bge import render
from uplogic.input.mouse import MOUSE
from uplogic.utils.math import clamp, map_range


class Slider(Widget):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 10.],
        relative={},
        halign='left',
        valign='bottom',
        orientation='horizontal',
        bar_width=.3,
        bar_color=(1, 1, 1, 1),
        bar_hover_color=(1, 1, 1, 1),
        knob_size=1,
        knob_color=(.8, .8, .8, 1),
        knob_hover_color=(.8, .8, .8, 1),
        steps=-1,
        allow_bar_click=True,
        angle=0
    ):
        super().__init__(pos, size, (0, 0, 0, 0), relative, halign=halign, valign=valign, angle=angle)
        self._value = 0
        self.border_width = 1
        self.border_color = (0, 0, 0, 1)
        self._horiz = orientation != 'vertical'
        bar_size = (1, bar_width) if self._horiz else (bar_width, 1)
        self.bar = Button(
            pos=(.5, .5),
            size=bar_size,
            valign='center',
            halign='center',
            relative={'size': True, 'pos': True},
            bg_color=bar_color,
            hover_color=bar_hover_color
        )
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
        self._build_shader()

    def _build_shader(self):
        super()._build_shader()
        if self.parent:
            self.value = self.value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        newval = value
        if self.steps > 0:
            newval -= newval % (1 / self.steps)
        newval = clamp(newval)
        if newval != self._value:
            self._value = newval
            self.on_value(self)
        knob_size = (self.knob._draw_size[self._slide_axis] * .5)
        self.knob.pos[self._slide_axis] = map_range(self._value, 0, 1, knob_size + self.border_width * .5, self._draw_size[self._slide_axis] - knob_size - self.border_width * .5)
        size = self._draw_size
        self.knob.pos[self._up_axis] = (size[1] * .5) if self._horiz else (size[0] * .5)
        knob_width = (size[1] if self._horiz else size[0])
        self.knob.size = (knob_width * self.knob_size - self.border_width, knob_width * self.knob_size - self.border_width)

    # def draw(self):
    #     super().draw()

    def _on_press(self, widget):
        pos = self._draw_pos
        knob_size = self.knob._draw_size[self._slide_axis] * .5
        step_size = (self._draw_size[self._slide_axis] / self.steps) * .5 if self.steps > 0 else 0
        self.value = map_range(
            (MOUSE.position.x * render.getWindowWidth() + step_size if self._horiz else (1 - MOUSE.position.y) * render.getWindowHeight() + step_size),
            pos[self._slide_axis] + knob_size,
            pos[self._slide_axis] + self._draw_size[self._slide_axis] - knob_size,
            0,
            1
        )

    def on_hold(self, widget):
        pass

    def on_release(self, widget):
        pass

    def on_hover(self, widget):
        pass

    def on_value(self, widget):
        pass


class FrameSlider(Slider):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 10.],
        relative={},
        halign='left',
        valign='bottom',
        orientation='horizontal',
        border_width=1,
        border_color=(.8, .8, .8, 1),
        bg_color=(0, 0, 0, 0),
        bar_color=(1, 1, 1, 1),
        bar_hover_color=(.1, .1, .1, .3),
        steps=-1,
        allow_bar_click=True,
        angle=0
    ):
        Widget.__init__(self, pos, size, (0, 0, 0, 0), relative, halign=halign, valign=valign, angle=angle)
        self._value = 0
        self._horiz = orientation != 'vertical'
        self.bar = Button(
            pos=(.5, .5),
            size=(1, 1),
            valign='center',
            halign='center',
            relative={'size': True, 'pos': True},
            border_color=border_color,
            bg_color=bg_color,
            border_width=border_width,
            hover_color=bar_hover_color
        )
        self.border_color = border_color
        self.border_width = border_width
        self._slide_axis = 0 if self._horiz else 1
        self._up_axis = 1 if self._horiz else 0
        self.knob_size = 1
        if allow_bar_click:
            self.bar.on_hold = self._on_press
        self.knob = RelativeLayout(size=(1, 1), bg_color=bar_color, valign='center', halign='center')
        self.add_widget(self.bar)
        self.add_widget(self.knob)
        self.steps = steps
        self.value = 0
        self._clicked = False
        self._released = False
        self._in_focus = False
        self._down = False


class ProgressSlider(FrameSlider):

    def __init__(self, pos=[0, 0], size=[100, 10], relative={}, halign='left', valign='bottom', orientation='horizontal', border_width=1, border_color=(0.8, 0.8, 0.8, 1), bg_color=(0, 0, 0, 0), bar_color=(1, 1, 1, 1), bar_hover_color=(0.1, 0.1, 0.1, 0.3), steps=-1, allow_bar_click=True, angle=0):
        super().__init__(pos, size, relative, halign, valign, orientation, border_width, border_color, bg_color, bar_color, bar_hover_color, steps, allow_bar_click, angle)
        self.knob.relative = {'size': True}
        self.knob.halign = 'left'
        self.knob.valign = 'bottom'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        newval = value
        if self.steps > 0:
            newval -= newval % (1 / self.steps)
        newval = clamp(newval)
        if newval != self._value:
            self._value = newval
            self.on_value(self)
        ds = self._draw_size
        width_sub = self.border_width / ds[0]
        height_sub = self.border_width / ds[1]
        self.knob.size = (clamp(self._value - width_sub), 1 - height_sub) if self._horiz else (1 - width_sub, clamp(self._value - height_sub))
        if self.border_width and self.border_color[3] > 0:
            self.knob.y = self.border_width * .5
            self.knob.x = self.border_width * .5

    def _on_press(self, widget):
        pos = self._draw_pos
        step_size = (self._draw_size[self._slide_axis] / self.steps) * .5 if self.steps > 0 else 0
        self.value = map_range(
            (MOUSE.position.x * render.getWindowWidth() + step_size if self._horiz else (1 - MOUSE.position.y) * render.getWindowHeight() + step_size),
            pos[self._slide_axis],
            pos[self._slide_axis] + self._draw_size[self._slide_axis],
            0,
            1
        )

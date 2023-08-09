from .widget import Widget
from .behaviors import HoverBehavior
from .label import Label
from .image import Image
from .image import Sprite
import gpu
from uplogic.input.mouse import MOUSE_EVENTS, LMB, RMB
from uplogic.utils import debug


class Button(Widget, HoverBehavior):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 100.],
        bg_color=(0, 0, 0, 0),
        relative={},
        border_width=1.0,
        border_color=(0, 0, 0, 0),
        hover_color=(0, 0, 0, .5),
        halign='left',
        valign='bottom',
        on_press=None,
        angle=0
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle)
        self.hover_color = hover_color
        self.border_width = border_width
        self.border_color = border_color
        self._clicked = False
        self._released = False
        self._in_focus = False
        self._down = False
        if on_press is not None:
            self.on_press = on_press

    def draw(self):
        super()._setup_draw()

        self._released = False
        self._clicked = False
        gpu.state.line_width_set(self.border_width)
        gpu.state.point_size_set(self.border_width)
        self._shader.uniform_float("color", self.hover_color if self._in_focus else self.bg_color)
        self._batch.draw(self._shader)
        self._shader.uniform_float("color", self.border_color)
        self._batch_line.draw(self._shader)
        self._batch_points.draw(self._shader)
        super().draw()

    def _evaluate(self):
        if self.hover:
            self._in_focus = True
            self.on_hover(self)
            self.canvas._hover_consumed = True
        else:
            self._in_focus = False
        if self._in_focus and MOUSE_EVENTS[LMB].active and not self.canvas._click_consumed:
            self.on_click(self)
            self.on_press(self)
            self._clicked = True
            self.canvas._click_consumed = True
            self._down = True
        elif not MOUSE_EVENTS[LMB].active and self._down:
            self.on_release(self)
            self._down = False
            self._released = True
            self.canvas._click_consumed = False
        elif self._down:
            self.on_hold(self)
        

    def on_click(self, widget):
        pass
        # debug(f'{self} clicked.')

    def on_press(self, widget):
        pass

    def on_hold(self, widget):
        pass
        # debug(f'{self} is being held.')

    def on_release(self, widget):
        pass
        # debug(f'{self} is released.')

    def on_hover(self, widget):
        pass
        # debug(f'{self} is hovered over.')


class LabelButton(Button, HoverBehavior):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 100.],
        relative={},
        bg_color=(0, 0, 0, 0),
        border_width=1.0,
        border_color=(0, 0, 0, 0),
        hover_color=(0, 0, 0, .5),
        text='',
        text_pos=[.5, .5],
        font='',
        font_size=12,
        font_color=(1, 1, 1, 1),
        line_height=1.5,
        halign='left',
        valign='bottom',
        halign_text='center',
        valign_text='center',
        on_press=None,
        angle=0
    ):
        self.label = Label(
            relative={'pos': True},
            pos=text_pos,
            font=font,
            halign=halign_text,
            valign=valign_text,
            text=text,
            font_color=font_color,
            font_size=font_size,
            line_height=line_height
        )
        super().__init__(
            pos,
            size,
            bg_color,
            relative,
            border_width=border_width,
            border_color=border_color,
            hover_color=hover_color,
            halign=halign,
            valign=valign,
            angle=angle,
            on_press=on_press
        )
        self.add_widget(self.label)
        self._in_focus = False

    @property
    def text(self):
        return self.label.text

    @text.setter
    def text(self, val):
        self.label.text = val

    @property
    def text_pos(self):
        return self.label.pos

    @text_pos.setter
    def text_pos(self, val):
        self.label.pos = val

    @property
    def font(self):
        return self.label.font

    @font.setter
    def font(self, val):
        self.label.font = val

    @property
    def font_size(self):
        return self.label.font_size

    @text.setter
    def font_size(self, val):
        self.label.font_size = val

    @property
    def font_color(self):
        return self.label.font_color

    @font_color.setter
    def font_color(self, val):
        self.label.font_color = val

    @property
    def line_height(self):
        return self.label.line_height

    @line_height.setter
    def line_height(self, val):
        self.label.line_height = val

    @property
    def halign_text(self):
        return self.label.halign

    @halign_text.setter
    def halign_text(self, val):
        self.label.halign = val

    @property
    def valign_text(self):
        return self.label.valign

    @valign_text.setter
    def valign_text(self, val):
        self.label.valign = val


class ImageButton(Button, HoverBehavior):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 100.],
        bg_color=(0, 0, 0, 0),
        border_color=(0, 0, 0, 0),
        hover_color=(0, 0, 0, .0),
        relative={},
        halign='left',
        valign='bottom',
        on_press=None,
        texture=None,
        angle=0
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, on_press=on_press, hover_color=hover_color, border_color=border_color)
        self.image = Image(relative={'size': True}, size=(1, 1), texture=texture)
        self.add_widget(self.image)

    @property
    def texture(self):
        return self.image.texture

    @texture.setter
    def texture(self, val):
        self.image.texture = val


class SpriteButton(Button, HoverBehavior):

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 100.],
        bg_color=(0, 0, 0, 0),
        border_color=(0, 0, 0, 0),
        hover_color=(0, 0, 0, .0),
        relative={},
        halign='left',
        valign='bottom',
        texture=None,
        idx=0,
        rows=1,
        cols=1,
        on_press=None,
        angle=0
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, on_press=on_press, hover_color=hover_color, border_color=border_color)
        self.image = Sprite(relative={'size': True}, size=(1, 1), texture=texture, rows=rows, cols=cols, idx=idx)
        self.add_widget(self.image)

    @property
    def texture(self):
        return self.image.texture

    @texture.setter
    def texture(self, val):
        self.image.texture = val

    @property
    def idx(self):
        return self.image.idx

    @idx.setter
    def idx(self, val):
        self.image.idx = val

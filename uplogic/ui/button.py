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
        click_color=(0, 0, 0, 0),
        halign='left',
        valign='bottom',
        on_press=None,
        angle=0
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle)
        self.hover_color = hover_color
        self.border_width = border_width
        self.border_color = border_color
        self.click_color = click_color
        self.override_color = None
        self._clicked = False
        self._released = False
        self._in_focus = False
        self._down = False
        self._hover = False
        if on_press is not None:
            self.on_press = on_press
        self.start()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, val):
        self._border_color = list(val)

    @property
    def click_color(self):
        return self._click_color

    @click_color.setter
    def click_color(self, val):
        self._click_color = list(val)

    @property
    def hover_color(self):
        return self._hover_color

    @hover_color.setter
    def hover_color(self, val):
        self._hover_color = list(val)

    @property
    def current_color(self):
        return self.click_color if self._clicked or self._down else (self.hover_color if self._in_focus else self.bg_color).copy()

    def draw(self):
        super()._setup_draw()
        self._released = False
        gpu.state.line_width_set(self.border_width)
        gpu.state.point_size_set(self.border_width)
        col = self.override_color if self.override_color is not None else self.current_color
        col[3] *= self.opacity
        bcol = self.border_color.copy()
        bcol[3] *= self.opacity
        self._shader.uniform_float("color", col)
        self._clicked = False
        self._batch.draw(self._shader)
        self._shader.uniform_float("color", bcol)
        self._batch_line.draw(self._shader)
        self._batch_points.draw(self._shader)
        super().draw()

    def evaluate(self):
        is_hover = self.hover
        was_hover = self._hover
        if is_hover and not was_hover:
            self.on_enter(self)
        elif was_hover and not is_hover:
            self.on_exit(self)
        self._hover = self.hover
        if self._hover:
            self._in_focus = True
            self.on_hover(self)
            self.canvas._hover_consumed = True
        else:
            self._in_focus = False
        if self._in_focus and MOUSE_EVENTS[LMB].active and not self.canvas._click_consumed and not self._down:
            self.on_click(self)
            self.on_press(self)
            self._clicked = True
            self.canvas._click_consumed = True
            self._down = True
        elif not MOUSE_EVENTS[LMB].active and self._down:
            self.on_release(self)
            self._down = False
            self._released = True
        elif self._down:
            self.canvas._click_consumed = True
            self.on_hold(self)
        self.override_color = None

    def on_enter(self, widget):
        pass

    def on_exit(self, widget):
        pass

    def on_click(self, widget):
        pass

    def on_press(self, widget):
        pass

    def on_hold(self, widget):
        pass

    def on_release(self, widget):
        pass

    def on_hover(self, widget):
        pass


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
        click_color=(0, 0, 0, 0),
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
        text_rel = relative.get('font_size', False)
        self.label = Label(
            relative={'pos': True, 'font_size': text_rel},
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
            click_color=click_color,
            halign=halign,
            valign=valign,
            angle=angle,
            on_press=on_press
        )
        self.add_widget(self.label)
        self._in_focus = False
        self.start()

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
        click_color=(0, 0, 0, 0),
        relative={},
        halign='left',
        valign='bottom',
        on_press=None,
        texture=None,
        hover_texture=None,
        click_texture=None,
        angle=0
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, on_press=on_press, hover_color=hover_color, border_color=border_color, click_color=click_color)
        self.image = Image(relative={'size': True}, size=(1, 1), texture=texture)
        self._texture_name = texture
        self.idle_texture = texture
        self.hover_texture = hover_texture if hover_texture else texture
        self.click_texture = click_texture if click_texture else texture
        self.add_widget(self.image)
        self.start()

    @property
    def texture(self):
        return self.image.texture

    @texture.setter
    def texture(self, val):
        self._texture_name = val
        self.image.texture = val

    @property
    def current_texture(self):
        return self.click_texture if self._clicked else (
            self.hover_texture if self._hover else self.idle_texture
        )

    def evaluate(self):
        super().evaluate()
        tex = self.current_texture
        if self._texture_name != tex:
            self.texture = tex


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
        hover_texture=None,
        click_texture=None,
        idx=0,
        rows=1,
        cols=1,
        on_press=None,
        angle=0
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, on_press=on_press, hover_color=hover_color, border_color=border_color)
        self.image = Sprite(relative={'size': True}, size=(1, 1), texture=texture, rows=rows, cols=cols, idx=idx)
        self._texture_name = texture

        self.idle_texture = texture
        self.hover_texture = hover_texture if hover_texture else texture
        self.click_texture = click_texture if click_texture else texture
        self.add_widget(self.image)
        self.start()

    @property
    def texture(self):
        return self.image.texture

    @texture.setter
    def texture(self, val):
        self._texture_name = val
        self.image.texture = val

    @property
    def current_texture(self):
        return self.click_texture if self._clicked else (
            self.hover_texture if self._hover else self.idle_texture
        )

    @property
    def idx(self):
        return self.image.idx

    @idx.setter
    def idx(self, val):
        self.image.idx = val

    def evaluate(self):
        super().evaluate()
        tex = self.current_texture
        if self._texture_name != tex:
            self.texture = tex
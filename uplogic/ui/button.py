from .widget import Widget
from .layout import RelativeLayout
from .behaviors import HoverBehavior
from .label import Label
from .image import Image
from .image import Sprite
import gpu
from uplogic.input.mouse import MOUSE_EVENTS, LMB, RMB
from uplogic import console
from mathutils import Vector


'''Button widgets for uplogic UI.'''


class Button(Widget, HoverBehavior):
    '''Clickable rectangular widget with hover, press, and release states.

    Mixes :class:`~uplogic.ui.widget.Widget` and
    :class:`~uplogic.ui.behaviors.HoverBehavior`.  Override the ``on_*``
    methods to react to interaction events.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param bg_color: Default background colour.
    :param relative: Relative positioning/sizing flags.
    :param border_width: Border thickness in pixels.
    :param border_color: Border colour.
    :param hover_color: Background colour while the cursor is over the widget.
    :param click_color: Background colour while the mouse button is held.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param on_press: Optional callable assigned to :meth:`on_press` at construction.
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

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
        angle=0,
        show=True
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, show=show)
        self.hover_color = Vector(hover_color)
        self.border_width = border_width
        self.border_color = Vector(border_color)
        self.click_color = Vector(click_color)
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
    def clicked(self):
        '''``True`` for one frame after an LMB press (and the widget is visible).'''
        return self._clicked and self.show

    @property
    def in_focus(self):
        '''``True`` while the cursor hovers over this widget.'''
        return self._hover and self.show

    @property
    def released(self):
        '''``True`` for one frame after the mouse button is released.'''
        return self._released and self.show

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
        '''Background colour displayed while the cursor is over the widget.'''
        return self._hover_color

    @hover_color.setter
    def hover_color(self, val):
        self._hover_color = list(val)

    @property
    def current_color(self):
        '''Active background colour: ``click_color`` when pressed, ``hover_color`` when focused, else ``bg_color``.'''
        return self.click_color if self._clicked or self._down else (self.hover_color if self._in_focus else self.bg_color).copy()

    def draw(self):
        self._setup_draw()
        self._released = False
        col = self.override_color if self.override_color is not None else self.current_color
        col[3] *= self.opacity
        self._shader.uniform_float("color", col)
        self._clicked = False
        self._batch.draw(self._shader)
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
        elif self._in_focus and MOUSE_EVENTS[RMB].active and not self.canvas._click_consumed and not self._down:
            self.on_right_click(self)
            self.on_right_press(self)
            self.canvas._click_consumed = True
            self._down = True
        elif not MOUSE_EVENTS[LMB].active and not MOUSE_EVENTS[RMB].active and self._down:
            self.on_release(self)
            self._down = False
            self._released = True
        elif self._down:
            self.canvas._click_consumed = True
            self.on_hold(self)
        self.override_color = None

    def on_enter(self, widget):
        '''Override to react to the cursor entering the widget area.'''
        pass

    def on_exit(self, widget):
        '''Override to react to the cursor leaving the widget area.'''
        pass

    def on_right_click(self, widget):
        '''Override to react to an initial RMB press over this widget.'''
        pass

    def on_right_press(self, widget):
        '''Override to react to an RMB press (fired on the same frame as :meth:`on_right_click`).'''
        pass

    def on_click(self, widget):
        '''Override to react to an initial LMB press over this widget.'''
        pass

    def on_press(self, widget):
        '''Override to react to an LMB press (fired on the same frame as :meth:`on_click`).'''
        pass

    def on_hold(self, widget):
        '''Override to react to a held LMB while focused (fired every frame).'''
        pass

    def on_release(self, widget):
        '''Override to react to LMB release.'''
        pass

    def on_hover(self, widget):
        '''Override to react to the cursor hovering over this widget (fired every frame).'''
        pass


class LabelButton(Button, HoverBehavior):
    '''A :class:`Button` with an embedded :class:`~uplogic.ui.label.Label` child.

    All label-related attributes delegate to the internal ``label`` widget.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param relative: Relative positioning/sizing flags.
    :param bg_color: Background colour.
    :param border_width: Border thickness in pixels.
    :param border_color: Border colour.
    :param hover_color: Hover background colour.
    :param click_color: Click background colour.
    :param text: Button label text.
    :param text_pos: Relative position ``[x, y]`` of the label within the button.
    :param font: Font file path.
    :param font_size: Font size in pt.
    :param font_color: Label text colour.
    :param line_height: Label line height factor.
    :param halign: Widget horizontal alignment.
    :param valign: Widget vertical alignment.
    :param halign_text: Label horizontal text alignment.
    :param valign_text: Label vertical text alignment.
    :param on_press: Optional press callback.
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

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
        angle=0,
        show=True
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
            on_press=on_press,
            show=show
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
    '''A :class:`Button` that displays a texture and swaps textures on hover/click.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param bg_color: Background colour.
    :param border_color: Border colour.
    :param hover_color: Hover tint colour.
    :param click_color: Click tint colour.
    :param relative: Relative positioning/sizing flags.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param on_press: Optional press callback.
    :param texture: Default (idle) texture path.
    :param hover_texture: Texture shown while hovered (defaults to *texture*).
    :param click_texture: Texture shown while clicked (defaults to *texture*).
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

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
        angle=0,
        show=True
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, on_press=on_press, hover_color=hover_color, border_color=border_color, click_color=click_color, show=show)
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
        '''Active texture path: ``click_texture`` when pressed, ``hover_texture`` when hovered, else ``idle_texture``.'''
        return self.click_texture if self._clicked else (
            self.hover_texture if self._hover else self.idle_texture
        )

    def evaluate(self):
        super().evaluate()
        tex = self.current_texture
        if self._texture_name != tex:
            self.texture = tex


class SpriteButton(Button, HoverBehavior):
    '''A :class:`Button` using a :class:`~uplogic.ui.image.Sprite` sheet with optional texture swaps on hover/click.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param bg_color: Background colour.
    :param border_color: Border colour.
    :param hover_color: Hover colour.
    :param relative: Relative positioning/sizing flags.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param texture: Sprite sheet image path.
    :param hover_texture: Texture on hover (defaults to *texture*).
    :param click_texture: Texture on click (defaults to *texture*).
    :param idx: Initial sprite sheet cell index.
    :param rows: Sprite sheet rows.
    :param cols: Sprite sheet columns.
    :param on_press: Optional press callback.
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

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
        angle=0,
        show=True
    ):
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, on_press=on_press, hover_color=hover_color, border_color=border_color, show=show)
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
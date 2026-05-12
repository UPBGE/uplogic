'''Scrollable container widget for uplogic UI.'''

from .layout import RelativeLayout
from .layout import ScrollBoxLayout
from .slider import FrameSlider
from uplogic.input.mouse import mouse_wheel
from uplogic.utils.math import map_range
from uplogic.utils.math import clamp, lerp
from uplogic import console
from bge import logic
from bge import render
from uplogic import events


class ScrollView(RelativeLayout):
    '''Scrollable container with an optional scroll bar.

    Children should be added via the inherited :meth:`add_widget`; they are
    placed inside an internal ``content_layout`` that grows to fit them.
    Mouse-wheel events inside the widget boundary scroll the content
    smoothly (animated via :attr:`seek_speed`).

    Clipping is always enabled and cannot be disabled.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param bg_color: Background colour.
    :param relative: Relative positioning/sizing flags.
    :param border_width: Border thickness in pixels.
    :param border_color: Border colour.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param scroll_speed: Pixels per mouse-wheel step.  Defaults to ``30``.
    :param use_scroll_bar: Whether to show the scroll bar.  Defaults to
        ``True``.
    :param scroll_bar_width: Scroll bar width in pixels.  Defaults to ``5``.
    :param scroll_bar_color: Scroll bar track colour.
    :param scroll_bar_knob_color: Scroll bar knob colour.
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

    def __init__(
        self,
        pos: list = [0, 0],
        size: list = [100, 100],
        bg_color: list = [0, 0, 0, 0],
        relative: dict = {},
        border_width: int = 1,
        border_color: list = [0, 0, 0, 0],
        halign: str = 'left',
        valign: str = 'bottom',
        scroll_speed=30,
        use_scroll_bar=True,
        scroll_bar_width=5,
        scroll_bar_color=(0, 0, 0, .8),
        scroll_bar_knob_color=(.8, .5, .1, 1),
        angle=0,
        show=True
    ):
        super().__init__(pos, size, bg_color, relative, border_width, border_color, halign, valign, angle, show)
        self.scroll_speed = scroll_speed
        self.use_scroll_bar = use_scroll_bar
        self.scroll_bar = FrameSlider(orientation='vertical', halign='right', size=(0, 0), bg_color=(0, 0, 0, 0), border_color=(0, 0, 0, 0), bar_hover_color=scroll_bar_color)
        self.scroll_bar.knob_color = scroll_bar_knob_color
        self.scroll_bar.square_knob = False
        self.scroll_bar_width = scroll_bar_width
        self.seek_speed = .2
        self.target_position = 0

        self.content_layout = RelativeLayout(valign='top', relative={'pos': True}, pos=(0, 1))
        self.add_widget(self.content_layout)
        self.add_widget(self.scroll_bar)
        self.remove_widget = self.content_layout.remove_widget
        self.add_widget = self.content_layout.add_widget

        self.scroll_bar.value = 0

    @property
    def use_clipping(self):
        '''Always ``True``; clipping cannot be disabled on :class:`ScrollView`.'''
        return True

    @use_clipping.setter
    def use_clipping(self, val):
        console.debug("'ScrollBoxLayout.use_clipping' is read-only!")

    @property
    def scroll_position_actual(self):
        '''Current animated scroll position in ``[0.0, 1.0]`` (0 = top, 1 = bottom).'''
        return map_range(self.content_layout.child_offset[1], 0, self._height_diff, 1, 0) if self._height_diff > 0 else 0

    def evaluate(self):
        mpos = logic.mouse.position
        if self.check_inside(mpos[0] * render.getWindowWidth(), mpos[1] * render.getWindowHeight()):
            self.scroll(mouse_wheel())
        self.content_layout.child_offset[1] = lerp(self.content_layout.child_offset[1], self.target_position, self.seek_speed)

        self.content_layout.height = self.content_layout.content_height
        self.content_layout.width = self.width_pixel
        self.scroll_bar.size = [self.scroll_bar_width, self.height]
        self.scroll_bar.y = -self.child_offset[1]
        self.scroll_bar.x = self.width
        self.scroll_bar.knob_size = [1, clamp(map_range(self._height_diff, 0, self.height_pixel * 3, 1, 0), 0.05, 1)]
        self.scroll_bar.set_value(self.scroll_position_actual)
        self.scroll_bar.show = self.scroll_bar.knob_size[1] < 1

    @property
    def _height_diff(self):
        return self.content_height - self.height_pixel

    def scroll(self, difference):
        '''Advance the scroll target by ``difference * scroll_speed`` pixels.

        :param difference: Signed scroll delta (positive = scroll down).
            Typically the value returned by
            :func:`~uplogic.input.mouse.mouse_wheel`.
        '''
        if difference != 0:
            self.target_position = clamp(self.target_position - difference * self.scroll_speed, 0, self._height_diff)
            self.scroll_bar._rebuild = True

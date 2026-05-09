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
        return True

    @use_clipping.setter
    def use_clipping(self, val):
        console.debug("'ScrollBoxLayout.use_clipping' is read-only!")

    @property
    def scroll_position_actual(self):
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
        if difference != 0:
            self.target_position = clamp(self.target_position - difference * self.scroll_speed, 0, self._height_diff)
            self.scroll_bar._mark_for_rebuild()
        
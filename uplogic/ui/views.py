from .layout import RelativeLayout
from .layout import ScrollBoxLayout
from .slider import FrameSlider
from uplogic.input.mouse import mouse_wheel
from uplogic.utils.math import map_range
from uplogic.utils.math import clamp
from bge import logic
from bge import render


class ScrollView(RelativeLayout):

    def __init__(
        self,
        pos: list = [0, 0],
        size: list = [100, 100],
        bg_color: list = [0, 0, 0, 0],
        relative: dict = {},
        border_width: int = 1,
        border_color: list = [0, 0, 0, 0],
        inverted: bool = False,
        spacing: int = 0,
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
        self.scroll_box = ScrollBoxLayout(orientation='vertical', relative={'size': True}, size=(1, 1), spacing=spacing, inverted=inverted)
        super().__init__(pos, size, bg_color, relative, border_width, border_color, halign, valign, angle, show)
        self.scroll_speed = scroll_speed
        self.use_scroll_bar = use_scroll_bar
        self.scroll_bar = FrameSlider(orientation='vertical', pos=(1, 0), relative={'pos': True}, halign='right', size=(0, 0), bg_color=(0, 0, 0, 0), border_color=(0, 0, 0, 0), bar_hover_color=scroll_bar_color)
        self.scroll_bar.square_knob = False
        self.scroll_bar_width = scroll_bar_width
        self.scroll_bar.on_value = self._on_scroll_bar
        self.add_widget(self.scroll_box)
        self.add_widget(self.scroll_bar)
        self.scroll_box._count_children = self._count_children
        self.remove_widget = self.scroll_box.remove_widget
        self.add_widget = self.scroll_box.add_widget
        self.scroll = self.scroll_box.scroll
        self.scroll_bar.value = 0

    @property
    def spacing(self):
        return self.scroll_box.spacing

    @spacing.setter
    def spacing(self, val):
        self.scroll_box.spacing = val

    @property
    def seek_speed(self):
        return self.scroll_box.seek_speed

    @seek_speed.setter
    def seek_speed(self, val):
        self.scroll_box.seek_speed = val

    def _on_scroll_bar(self, widget):
        self.scroll_box.scroll_position = self.scroll_bar.value

    def _count_children(self):
        ScrollBoxLayout._count_children(self.scroll_box)
        self.scroll_bar.knob_size = [1, clamp(map_range(self.scroll_box._height_diff, 0, self.height_pixel * 3, 1, 0), 0.05, 1)]
        self.scroll_bar.show = self.scroll_box._height_diff >= 0 and self.use_scroll_bar
        self.scroll_bar.size = [self.scroll_bar_width, self.height_pixel]
        # self.scroll_bar.set_value(self.scroll_box.scroll_position_actual)

    # def evaluate(self):
    #     super().evaluate()

    def evaluate(self):
        mpos = logic.mouse.position
        if self.check_inside(mpos[0] * render.getWindowWidth(), mpos[1] * render.getWindowHeight()):
            self.scroll(mouse_wheel())
        if not self.scroll_bar.bar._down:
            self.scroll_bar.set_value(self.scroll_box.scroll_position_actual)

    def scroll(self, difference):
        if difference != 0:
            self.scroll_box.scroll(difference)
        
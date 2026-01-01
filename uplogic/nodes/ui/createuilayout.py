from uplogic.nodes import ULActionNode
from uplogic.ui import RelativeLayout, FloatLayout, BoxLayout, GridLayout
from uplogic.ui import PolarLayout as _PolarLayout
from math import degrees


class PolarLayout(_PolarLayout):
    def __init__(
        self,
        pos: list = (0, 0),
        size=(0, 0),
        bg_color=(0, 0, 0, 0),
        border_width=0,
        border_color=(0, 0, 0, 0),
        halign='center',
        valign='center',
        relative: dict = {},
        starting_angle: str = 0,
        radius: int = 100,
        angle: float = 0
    ):
        super().__init__(pos, relative, starting_angle, radius, angle)

layouts = {
    'FloatLayout': FloatLayout,
    'RelativeLayout': RelativeLayout,
    'BoxLayout': BoxLayout,
    'GridLayout': GridLayout,
    'PolarLayout': PolarLayout
}


class ULCreateUILayout(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.parent = None
        self.rel_pos = False
        self.pos = (0, 0)
        self.rel_size = False
        self.size = (100, 100)
        self.angle = 0
        self.color = (0, 0, 0, 0)
        self.border_width = 0
        self.border_color = (0, 0, 0, 0)
        self.spacing = 0
        self.inverted = False
        self.cols = 1
        self.rows = 1
        self.starting_angle = 0
        self.radius = 100
        self._widget = None
        self.layout_type = 'RelativeLayout'
        self.boxlayout_type = 'vertical'
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self.OUT = self.add_output(self._get_done)
        self.WIDGET = self.add_output(self._get_widget)

    def _get_done(self):
        return self._done

    def _get_widget(self):
        return self._widget

    def evaluate(self):
        if not self.get_condition():
            return
        ipt = self.get_input
        parent = ipt(self.parent)
        rel_pos = ipt(self.rel_pos)
        pos = ipt(self.pos)
        rel_size = ipt(self.rel_size)
        size = ipt(self.size)
        angle = degrees(ipt(self.angle))
        color = ipt(self.color)
        border_width = ipt(self.border_width)
        border_color = ipt(self.border_color)

        self._widget = layouts[self.layout_type](
            pos=pos,
            size=size,
            bg_color=color,
            relative={'pos': rel_pos, 'size': rel_size},
            border_width=border_width,
            border_color=border_color,
            halign=self.halign_type,
            valign=self.valign_type,
            angle=angle
        )
        if self.layout_type == 'BoxLayout':
            self._widget.orientation = self.boxlayout_type
            self._widget.spacing = ipt(self.spacing)
        elif self.layout_type == 'GridLayout':
            self._widget.orientation = self.boxlayout_type
            self._widget.spacing = ipt(self.spacing)
            self._widget.cols = ipt(self.cols)
            self._widget.rows = ipt(self.rows)
        elif self.layout_type == 'PolarLayout':
            self._widget.starting_angle = self.starting_angle
            self._widget.radius = ipt(self.radius)
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

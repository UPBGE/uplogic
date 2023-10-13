from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import Slider, FrameSlider, ProgressSlider
from mathutils import Vector
from math import degrees


class ULCreateUISlider(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent = None
        self.rel_pos = None
        self.pos = None
        self.rel_size = None
        self.size = None
        self.relative = None
        self.angle = None
        self.bar_width = None
        self.border_width = None
        self.border_color = None
        self.bar_color = None
        self.bar_hover_color = None
        self.knob_size = None
        self.knob_color = None
        self.knob_hover_color = None
        self.steps = None
        self.allow_bar_click = None
        self._widget = None
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self.orientation_type = 'horizontal'
        self.slider_type = '0'
        self._done = False
        self.OUT = ULOutSocket(self, self._get_done)
        self.WIDGET = ULOutSocket(self, self._get_widget)
        self.VALUE = ULOutSocket(self, self._get_value)
        self.KNOB_POSITION = ULOutSocket(self, self._get_knob_pos)

    def _get_done(self):
        return self._done

    def _get_widget(self):
        return self._widget

    def _get_value(self):
        return self._widget.value if self._widget else 0

    def _get_knob_pos(self):
        return Vector(self._widget.knob.pos_abs) if self._widget else Vector((0, 0))

    def evaluate(self):
        self._done = False
        if not self.get_input(self.condition):
            return
        ipt = self.get_input

        parent = ipt(self.parent)

        if self.slider_type == '2':
            self._widget = ProgressSlider(
                pos=ipt(self.pos),
                size=ipt(self.size),
                relative={'pos': ipt(self.rel_pos), 'size': ipt(self.rel_size)},
                halign=ipt(self.halign_type),
                valign=ipt(self.valign_type),
                orientation=ipt(self.orientation_type),
                border_width=ipt(self.border_width),
                border_color=ipt(self.border_color),
                bg_color=ipt(self.bar_color),
                bar_color=ipt(self.knob_color),
                bar_hover_color=ipt(self.bar_hover_color),
                steps=ipt(self.steps),
                allow_bar_click=ipt(self.allow_bar_click),
                angle=degrees(ipt(self.angle))
            )
        elif self.slider_type == '1':
            self._widget = FrameSlider(
                pos=ipt(self.pos),
                size=ipt(self.size),
                relative={'pos': ipt(self.rel_pos), 'size': ipt(self.rel_size)},
                halign=ipt(self.halign_type),
                valign=ipt(self.valign_type),
                orientation=ipt(self.orientation_type),
                border_width=ipt(self.border_width),
                border_color=ipt(self.border_color),
                bg_color=ipt(self.bar_color),
                bar_color=ipt(self.knob_color),
                bar_hover_color=ipt(self.bar_hover_color),
                steps=ipt(self.steps),
                allow_bar_click=ipt(self.allow_bar_click),
                angle=degrees(ipt(self.angle))
            )
        else:
            self._widget = Slider(
                pos=ipt(self.pos),
                size=ipt(self.size),
                relative={'pos': ipt(self.rel_pos), 'size': ipt(self.rel_size)},
                halign=ipt(self.halign_type),
                valign=ipt(self.valign_type),
                orientation=ipt(self.orientation_type),
                bar_width=ipt(self.bar_width),
                # border_color=ipt(self.border_color),
                bar_color=ipt(self.bar_color),
                bar_hover_color=ipt(self.bar_hover_color),
                knob_size=ipt(self.knob_size),
                knob_color=ipt(self.knob_color),
                knob_hover_color=ipt(self.knob_hover_color),
                steps=ipt(self.steps),
                allow_bar_click=ipt(self.allow_bar_click),
                angle=degrees(ipt(self.angle))
            )
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

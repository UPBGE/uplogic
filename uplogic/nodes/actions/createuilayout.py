from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import RelativeLayout, FloatLayout, BoxLayout
from math import degrees


layouts = {
    'FloatLayout': FloatLayout,
    'RelativeLayout': RelativeLayout,
    'BoxLayout': BoxLayout
}


class ULCreateUILayout(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent = None
        self.rel_pos = None
        self.pos = None
        self.rel_size = None
        self.size = None
        self.angle = None
        self.color = None
        self.border_width = None
        self.border_color = None
        self.spacing = None
        self._widget = None
        self.layout_type = 'RelativeLayout'
        self.boxlayout_type = 'vertical'
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self._done = False
        self.OUT = ULOutSocket(self, self._get_done)
        self.WIDGET = ULOutSocket(self, self._get_widget)

    def _get_done(self):
        return self._done

    def _get_widget(self):
        return self._widget

    def evaluate(self):
        self._done = False
        if not self.get_input(self.condition):
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
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

from uplogic.nodes import ULActionNode
from uplogic.ui import Image
from math import degrees


class ULCreateUIImage(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent = None
        self.rel_pos = None
        self.pos = None
        self.rel_size = None
        self.size = None
        self.angle = None
        self.texture = None
        self._widget = None
        self.layout_type = 'RelativeLayout'
        self.boxlayout_type = 'vertical'
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self.aspect_ratio = True
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
        texture = ipt(self.texture)

        self._widget = Image(
            pos=pos,
            size=size,
            texture=texture.name,
            relative={'pos': rel_pos, 'size': rel_size},
            halign=self.halign_type,
            valign=self.valign_type,
            use_aspect_ratio=self.aspect_ratio,
            angle=angle
        )
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

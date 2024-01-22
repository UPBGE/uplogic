from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import Label
from math import degrees


class ULCreateUILabel(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent = None
        self.rel_pos = False
        self.pos = (0, 0)
        self.rel_size = False
        self.angle = 0
        self.text = ''
        self.text_pos = (0, 0)
        self.font = 0
        self.font_size = 12
        self.line_height = 1.4
        self.font_color = (1, 1, 1, 1)
        self.use_shadow = False
        self.shadow_offset = [2, 2]
        self.shadow_color = (0, 0, 0, 1)
        self._widget = None
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self._done = False
        self.OUT = self.add_output(self._get_done)
        self.WIDGET = self.add_output(self._get_widget)

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
        angle = degrees(ipt(self.angle))
        text = ipt(self.text)
        font = ipt(self.font)
        font_size = ipt(self.font_size)
        line_height = ipt(self.line_height)
        font_color = ipt(self.font_color)
        use_shadow = ipt(self.use_shadow)
        if use_shadow:
            shadow_offset = ipt(self.shadow_offset)
            shadow_color = ipt(self.shadow_color)
        else:
            shadow_offset = [0, 0]
            shadow_color = [0, 0, 0, 0]

        
        font = font.filepath.replace('\\', '/') if font else 0

        print(rel_pos)

        self._widget = Label(
            pos=pos,
            relative={'pos': rel_pos},
            halign=self.halign_type,
            valign=self.valign_type,
            text=text,
            font=font,
            font_size=font_size,
            line_height=line_height,
            font_color=font_color,
            shadow=use_shadow,
            shadow_offset=shadow_offset,
            shadow_color=shadow_color,
            angle=angle
        )
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

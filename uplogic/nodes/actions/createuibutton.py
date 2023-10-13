from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import LabelButton
from math import degrees


class ULCreateUIButton(ULActionNode):
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
        self.text = None
        self.text_pos = None
        self.font = None
        self.font_size = None
        self.font_color = None
        self.line_height = None
        self.hover_color = None
        self._clicked = False
        self._hovering = False
        self._released = False
        self._widget = None
        self._done = False
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self.text_halign_type = 'left'
        self.text_valign_type = 'bottom'
        self.OUT = ULOutSocket(self, self._get_done)
        self.WIDGET = ULOutSocket(self, self._get_widget)
        self.CLICK = ULOutSocket(self, self._get_click)
        self.HOVER = ULOutSocket(self, self._get_hover)
        self.RELEASE = ULOutSocket(self, self._get_release)

    def _get_done(self):
        return self._done

    def _get_widget(self):
        return self._widget

    def _get_click(self):
        w = self._widget
        if w:
            return w._clicked
        return False

    def _get_hover(self):
        w = self._widget
        if w:
            return w._in_focus
        return False

    def _get_release(self):
        w = self._widget
        if w:
            return w._released
        return False

    def evaluate(self):
        self._done = False
        condition = self.get_input(self.condition)
        if not condition:
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
        hover_color = ipt(self.hover_color)
        text = ipt(self.text)
        text_pos = ipt(self.text_pos)
        font = ipt(self.font)
        font_size = ipt(self.font_size)
        font_color = ipt(self.font_color)
        line_height = ipt(self.line_height)

        font = font.filepath.replace('\\', '/') if font else 0

        self._widget = LabelButton(
            pos=pos,
            size=size,
            bg_color=color,
            relative={'pos': rel_pos, 'size': rel_size},
            hover_color=hover_color,
            text=text,
            text_pos=text_pos,
            font=font,
            font_size=font_size,
            font_color=font_color,
            line_height=line_height,
            halign_text=self.text_halign_type,
            valign_text=self.text_valign_type,
            border_width=border_width,
            border_color=border_color,
            halign=self.halign_type,
            valign=self.valign_type,
            angle=angle
        )
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

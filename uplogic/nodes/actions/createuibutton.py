from uplogic.nodes import ULActionNode
from uplogic.ui import LabelButton
from math import degrees


class ULCreateUIButton(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent = None
        self.rel_pos = False
        self.pos = (0, 0)
        self.rel_size = False
        self.size = (100, 100)
        self.angle = 0
        self.color = (9, 0, 0, 0)
        self.border_width = 0
        self.border_color = (0, 0, 0, 0)
        self.text = ''
        self.text_pos = (0, 0)
        self.font = 0
        self.font_size = 12
        self.font_color = (1, 1, 1, 1)
        self.line_height = 1.4
        self.hover_color = (0, 0, 0, .5)
        self._clicked = False
        self._hovering = False
        self._released = False
        self._widget = None
        self.halign_type = 'left'
        self.valign_type = 'bottom'
        self.text_halign_type = 'left'
        self.text_valign_type = 'bottom'
        self.OUT = self.add_output(self._get_done)
        self.WIDGET = self.add_output(self._get_widget)
        self.CLICK = self.add_output(self._get_click)
        self.HOVER = self.add_output(self._get_hover)
        self.RELEASE = self.add_output(self._get_release)

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
        

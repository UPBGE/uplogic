from uplogic.nodes import ULActionNode
from uplogic.ui import Path
from math import degrees


class CreateUIPathNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.parent = None
        self.points = []
        self.rel_pos = False
        self.pos = (0, 0)
        self.rel_points = False
        self.angle = 0
        self.line_color = (9, 0, 0, 0)
        self.line_width = 0
        self._widget = None
        self.DONE = self.add_output(self._get_done)
        self.PATH = self.add_output(self._get_widget)

    def _get_done(self):
        return self._done

    def _get_widget(self):
        return self._widget

    def evaluate(self):
        condition = self.get_condition()
        if not condition:
            return
        ipt = self.get_input
        parent = ipt(self.parent)
        rel_pos = ipt(self.rel_pos)
        pos = ipt(self.pos)
        rel_points = ipt(self.rel_points)
        points = ipt(self.points)
        line_color = ipt(self.line_color)
        line_width = ipt(self.line_width)
        angle = degrees(ipt(self.angle))

        self._widget = Path(
            pos=pos,
            relative={'pos': rel_pos, 'points': rel_points},
            points=points,
            line_color=line_color,
            line_width=line_width,
            angle=angle
        )
        if parent:
            parent.add_widget(self._widget)
        self._done = True
        

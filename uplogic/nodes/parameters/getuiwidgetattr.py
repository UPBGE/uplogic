from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULGetUIWidgetAttr(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.widget = None
        self.widget_attr = 'show'
        self.BOOL = self.add_output(self._get_attr)
        self.COLOR = self.add_output(self._get_attr)
        self.ALPHA = self.add_output(self._get_attr)
        self.VEC2 = self.add_output(self._get_attr)
        self.STR = self.add_output(self._get_attr)
        self.INT = self.add_output(self._get_attr)
        self.FLOAT = self.add_output(self._get_attr)
        self.FONT = self.add_output(self._get_attr)
        self.IMG = self.add_output(self._get_attr)

    def _get_attr(self):
        widget = self.get_input(self.widget)
        return getattr(widget, self.widget_attr, None)

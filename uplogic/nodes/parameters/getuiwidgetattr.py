from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULGetUIWidgetAttr(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.widget = None
        self.widget_attr = 'show'
        self.BOOL = ULOutSocket(self, self._get_attr)
        self.COLOR = ULOutSocket(self, self._get_attr)
        self.ALPHA = ULOutSocket(self, self._get_attr)
        self.VEC2 = ULOutSocket(self, self._get_attr)
        self.STR = ULOutSocket(self, self._get_attr)
        self.INT = ULOutSocket(self, self._get_attr)
        self.FLOAT = ULOutSocket(self, self._get_attr)
        self.FONT = ULOutSocket(self, self._get_attr)
        self.IMG = ULOutSocket(self, self._get_attr)

    def _get_attr(self):
        widget = self.get_input(self.widget)
        return getattr(widget, self.widget_attr, None)

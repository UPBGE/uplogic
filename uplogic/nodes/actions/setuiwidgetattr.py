from uplogic.nodes import ULActionNode
from math import degrees
import bpy


class ULSetUIWidgetAttr(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.widget = None
        self.value = None
        self.widget_attr = 'show'
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        widget = self.get_input(self.widget)
        value = self.get_input(self.value)
        if self.widget_attr == 'angle':
            value = degrees(value)
        elif self.widget_attr == 'texture':
            value = value.name
        elif self.widget_attr == 'font':
            value = value.filepath.replace('\\', '/') if value else 0
        setattr(widget, self.widget_attr, value)
        self._done = True

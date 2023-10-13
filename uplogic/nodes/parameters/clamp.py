from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector


class ULClamp(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.range = None
        self.min_value = None
        self.max_value = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        value = self.get_input(self.value)
        if self.min_value is not None:
            range_ft = Vector((self.get_input(self.min_value), self.get_input(self.max_value)))
        else:
            range_ft = self.get_input(self.range)

        if range_ft.x == range_ft.y:
            return value
        if value < range_ft.x:
            value = range_ft.x
        if value > range_ft.y:
            value = range_ft.y
        return value

from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.math import map_range, map_range_vector


class ULMapRange(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.from_min = None
        self.from_max = None
        self.to_min = None
        self.to_max = None
        self.clamp = False
        self.mode = 0
        self.operations = [map_range, map_range_vector]
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.operations[self.mode](
            self.get_input(self.value),
            self.get_input(self.from_min),
            self.get_input(self.from_max),
            self.get_input(self.to_min),
            self.get_input(self.to_max),
            self.clamp
        )

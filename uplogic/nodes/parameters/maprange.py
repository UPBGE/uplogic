from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.constants import STATUS_WAITING
from uplogic.utils import is_invalid


class ULMapRange(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.from_min = None
        self.from_max = None
        self.to_min = None
        self.to_max = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        value = self.get_input(self.value)
        from_min = self.get_input(self.from_min)
        from_max = self.get_input(self.from_max)
        to_min = self.get_input(self.to_min)
        to_max = self.get_input(self.to_max)
        
        if is_invalid(value, from_min, from_max, to_min, to_max):
            return STATUS_WAITING
        
        from_value = from_max - from_min
        to_value = to_max - to_min
        
        return to_min + (((value - from_min) / from_value) * to_value)

    def evaluate(self):
        self._set_ready()
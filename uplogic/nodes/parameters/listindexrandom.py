from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
import random


class ULListIndexRandom(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.condition = None
        self._item = None
        self.items = None
        self.OUT = ULOutSocket(self, self.get_val)

    def get_val(self):
        list_d = self.get_input(self.items)
        self._item = random.choice(list_d)
        return self._item

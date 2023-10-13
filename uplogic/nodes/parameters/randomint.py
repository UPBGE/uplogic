

from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
import random
import sys


class ULRandomInt(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.max_value = None
        self.min_value = None
        self.OUT_A = ULOutSocket(self, self._get_output)

    def _get_output(self):
        min_value = self.get_input(self.min_value)
        max_value = self.get_input(self.max_value)
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        if min_value == max_value:
            min_value = -sys.maxsize
            max_value = sys.maxsize

        return random.randint(min_value, max_value)

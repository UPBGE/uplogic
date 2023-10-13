from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULConditionNode
from uplogic.utils.constants import LOGIC_OPERATORS
from mathutils import Vector


class ULCheckDistance(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.operation = 0
        self.param_a = None
        self.param_b = None
        self.dist = None
        self._distance = 0
        self.OUT = ULOutSocket(self, self.get_result)
        self.DIST = ULOutSocket(self, self.get_distance)

    def get_result(self):
        dist = self.get_input(self.dist)
        return LOGIC_OPERATORS[self.operation](self._distance, dist)

    def get_distance(self):
        return self._distance

    def evaluate(self):
        self._distance = (Vector(self.get_input(self.param_a)) - Vector(self.get_input(self.param_b))).length

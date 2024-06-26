from mathutils import Vector
from uplogic.nodes import ULConditionNode
from uplogic.utils.constants import LOGIC_OPERATORS
import math


class ULVectorAngleCheck(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.op: str = None
        self.vector: Vector = None
        self.vector_2: Vector = None
        self.value = None
        self._angle = 0
        self.OUT = self.add_output(self.get_done)
        self.ANGLE = self.add_output(self.get_angle)

    def get_angle(self):
        return self._angle

    def get_done(self):
        op: str = self.get_input(self.op)
        value: float = self.get_input(self.value)
        return LOGIC_OPERATORS[int(op)](self._angle, value)

    def evaluate(self):
        vector: Vector = self.get_input(self.vector)
        vector_2: Vector = self.get_input(self.vector_2)
        rad: float = vector.angle(vector_2)
        deg: float = rad * 180/math.pi
        self._angle = deg

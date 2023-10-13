from mathutils import Vector
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
import math


class ULVectorAngle(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.op = None
        self.vector: Vector = None
        self.vector_2: Vector = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        vector: Vector = self.get_input(self.vector)
        vector_2: Vector = self.get_input(self.vector_2)
        rad: float = vector.angle(vector_2)
        deg: float = rad * 180/math.pi
        return deg

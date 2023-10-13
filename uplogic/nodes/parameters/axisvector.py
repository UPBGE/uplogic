from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils.constants import LO_AXIS_TO_VECTOR


class ULAxisVector(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = ULOutSocket(self, self.get_vec)

    def get_vec(self):
        obj = self.get_input(self.game_object)
        front_vector = LO_AXIS_TO_VECTOR[self.axis]
        return obj.getAxisVect(front_vector)

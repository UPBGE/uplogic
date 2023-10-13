from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils import compute_distance


class ULDistance(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.parama = None
        self.paramb = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        parama = self.get_input(self.parama)
        paramb = self.get_input(self.paramb)
        return compute_distance(parama, paramb)

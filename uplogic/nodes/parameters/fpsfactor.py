from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils import FPS_FACTOR
from bge import logic


class ULFPSFactor(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.TIMEFACTOR = ULOutSocket(self, self.get_out)

    def get_out(self):
        return FPS_FACTOR()

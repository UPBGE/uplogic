from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils import FPS_FACTOR
from bge import logic


class ULFPSFactor(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.TIMEFACTOR = ULOutSocket(self, self.get_out)

    def get_out(self):
        socket = self.get_output('out')
        if socket is None:
            return self.set_output('out', FPS_FACTOR())
        return socket

    def evaluate(self):
        self._set_ready()

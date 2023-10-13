from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.nodes.logictree import ULLogicTree
from bge import logic


class ULTimeData(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.network: ULLogicTree = None
        self.TIME_PER_FRAME = ULOutSocket(
            self,
            self.get_time_per_frame
        )
        self.FPS = ULOutSocket(self, self.get_fps)
        self.TIMELINE = ULOutSocket(self, self.get_timeline)

    def get_time_per_frame(self):
        return self.network.time_per_frame

    def get_fps(self):
        tpf = self.network.time_per_frame or 1
        fps = logic.getAverageFrameRate()
        return fps if fps < 500 else 1 / tpf

    def get_timeline(self):
        return logic.getRealTime()

    def setup(self, network):
        self.network = network

    def evaluate(self):
        pass

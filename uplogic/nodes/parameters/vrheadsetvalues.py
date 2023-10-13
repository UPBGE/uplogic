from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.input import VRHeadset


class ULGetVRHeadsetValues(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.controller = VRHeadset()
        self.POS = ULOutSocket(self, self.get_pos)
        self.ORI = ULOutSocket(self, self.get_ori)

    def get_pos(self):
        return self.controller.position
    
    def get_ori(self):
        return self.controller.orientation.to_euler()

from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.input import ULControllerVR


class ULGetVRControllerValues(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self._index = None
        self.index = None
        self.controller = None
        self.POS = ULOutSocket(self, self.get_pos)
        self.ORI = ULOutSocket(self, self.get_ori)
        self.APOS = ULOutSocket(self, self.get_apos)
        self.AORI = ULOutSocket(self, self.get_aori)
        self.STICK = ULOutSocket(self, self.get_stick)
        self.TRIGGER = ULOutSocket(self, self.get_trigger)
    
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, val):
        self._index = val
        self.controller = ULControllerVR(self.index)

    def get_pos(self):
        return self.controller.position
    
    def get_ori(self):
        return self.controller.orientation.to_euler()
    
    def get_apos(self):
        return self.controller.position_aim
    
    def get_aori(self):
        return self.controller.orientation_aim.to_euler()
    
    def get_stick(self):
        return self.controller.thumbstick
    
    def get_trigger(self):
        return self.controller.trigger

    def evaluate(self):
        self._set_ready()

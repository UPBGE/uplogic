from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.input import VRController


class ULGetVRControllerValues(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self._index = None
        self.index = None
        self.controller = None
        self.POS = self.add_output(self.get_pos)
        self.ORI = self.add_output(self.get_ori)
        self.APOS = self.add_output(self.get_apos)
        self.AORI = self.add_output(self.get_aori)
        self.STICK = self.add_output(self.get_stick)
        self.TRIGGER = self.add_output(self.get_trigger)
    
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, val):
        self._index = val
        self.controller = VRController(self.index)

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

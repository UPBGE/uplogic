from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bge.types import KX_GameObject


class ULSetLightEnergy(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.lamp = None
        self.energy = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        light: KX_GameObject = self.get_input(self.lamp)
        energy = self.get_input(self.energy)
        light = light.blenderObject.data
        light.energy = energy
        self.done = True

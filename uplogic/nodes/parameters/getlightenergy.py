from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULGetLightEnergy(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.lamp = None
        self.energy = 0
        self.ENERGY = ULOutSocket(self, self.get_energy)

    def get_energy(self):
        lamp = self.get_input(self.lamp)
        light = lamp.blenderObject.data
        return light.energy

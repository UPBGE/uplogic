from uplogic.nodes import ULActionNode
from bge.types import KX_GameObject


class ULSetLightEnergy(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.lamp = None
        self.energy = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        light: KX_GameObject = self.get_input(self.lamp)
        energy = self.get_input(self.energy)
        light = light.blenderObject.data
        light.energy = energy
        self._done = True

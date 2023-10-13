from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.physics import RWD
from uplogic.utils.constants import VEHICLE


class ULVehicleApplyForce(ULActionNode):
    def __init__(self, value_type=RWD):
        ULActionNode.__init__(self)
        self.value_type = str(value_type)
        self.condition = None
        self.vehicle = None
        self.wheelcount = None
        self._reset = False
        self.power = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.vehicle)
        vehicle = game_object.get(VEHICLE, None)
        if vehicle is None:
            return
        value = self.get_input(self.value_type)
        wheelcount = self.get_input(self.wheelcount)
        power = self.get_input(self.power)
        vehicle.accelerate(power, value, wheelcount)
        self.done = True

from uplogic.nodes import ULActionNode
from uplogic.physics import RWD, Vehicle
from uplogic.utils.constants import VEHICLE


class ULVehicleApplyBraking(ULActionNode):
    def __init__(self, value_type=RWD):
        ULActionNode.__init__(self)
        self.value_type = str(value_type)
        self.condition = None
        self.vehicle = None
        self.wheelcount = None
        self._reset = False
        self.power = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.vehicle)
        vehicle: Vehicle = game_object.get(VEHICLE, None)
        if vehicle is None:
            return
        value_type = self.get_input(self.value_type)
        wheelcount = self.get_input(self.wheelcount)
        power = self.get_input(self.power)
        vehicle.brake(power, value_type, wheelcount)
        self._done = True

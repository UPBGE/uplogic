from uplogic.nodes import ULActionNode
from uplogic.physics.vehicle import Vehicle
from uplogic.utils.constants import VEHICLE


class ULCreateVehicle(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.suspension = None
        self.stiffness = None
        self.damping = None
        self.friction = None
        self.wheel_size = None
        self.vehicle = None
        self.OUT = self.add_output(self.get_done)
        self.VEHICLE = self.add_output(self.get_vehicle)
        self.WHEELS = self.add_output(self.get_wheels)

    def get_done(self):
        return self._done

    def get_vehicle(self):
        return self.vehicle

    def get_wheels(self):
        return self.vehicle.wheels

    def evaluate(self):
        game_object = self.get_input(self.game_object)
        if not self.get_condition():
            if game_object.get(VEHICLE):
                self.vehicle = game_object[VEHICLE]
            return
        suspension = self.get_input(self.suspension)
        stiffness = self.get_input(self.stiffness)
        damping = self.get_input(self.damping)
        friction = self.get_input(self.friction)
        wheel_size = self.get_input(self.wheel_size)
        self.vehicle = Vehicle(
            game_object,
            suspension,
            stiffness,
            damping,
            friction,
            wheel_size
        )
        self._done = True

from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULConditionNode


class ULSensorPositive(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.obj_name = None
        self.sens_name = None
        self.OUT = ULOutSocket(self, self.get_sensor)

    def get_sensor(self):
        game_obj = self.get_input(self.obj_name)
        sens_name = self.get_input(self.sens_name)
        return game_obj.sensors[sens_name].positive

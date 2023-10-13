from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULActionNode


class ULSetSensorValue(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_obj = None
        self.sens_name = None
        self.field = None
        self.value = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_obj = self.get_input(self.game_obj)
        sens_name = self.get_input(self.sens_name)
        # sensor = game_obj.blenderObject.game.sensors.get(sens_name)
        sensor = game_obj.sensors.get(sens_name)
        if not sensor:
            return
        field = self.get_input(self.field)
        value = self.get_input(self.value)
        setattr(sensor, field, value)
        self.done = True

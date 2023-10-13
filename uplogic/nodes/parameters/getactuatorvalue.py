from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULGetActuatorValue(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_obj = None
        self.act_name = None
        self.field = None
        self.OUT = ULOutSocket(self, self.get_actuator)

    def get_actuator(self):
        game_obj = self.get_input(self.game_obj)
        act_name = self.get_input(self.act_name)
        field = self.get_input(self.field)
        if act_name not in game_obj.actuators:
            return False
        return getattr(game_obj.actuators[act_name], field)

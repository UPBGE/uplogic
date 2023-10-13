from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from bge.types import KX_GameObject as GameObject


class ULGetSensorValue(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_obj = None
        self.sens_name = None
        self.field = None
        self.OUT = ULOutSocket(self, self.get_sensor)

    def get_sensor(self):
        game_obj: GameObject = self.get_input(self.game_obj)
        sens_name: str = self.get_input(self.sens_name)
        field = self.get_input(self.field)
        return getattr(game_obj.sensors[sens_name], field)

from uplogic.nodes import ULOutSocket, ULParameterNode
from uplogic.utils import STATUS_WAITING, is_invalid


class ULGetProperty(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.property_name = None
        self.mode = 'GAME'
        self.OUT = ULOutSocket(self, self.get_property)

    def get_property(self):
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        if is_invalid(game_object, property_name):
            return STATUS_WAITING
        props = (
            game_object.getPropertyNames()
            if self.mode == 'GAME' else
            [p[0] for p in game_object.blenderObject.items()]
        )
        if property_name in props:
            obj = game_object if self.mode == 'GAME' else game_object.blenderObject
            return obj.get(property_name)
        game_object[property_name] = None

    def evaluate(self):
        self._set_ready()

from uplogic.nodes import ULOutSocket, ULParameterNode


class ULGetProperty(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.property_name = None
        self.mode = 0
        self.OUT = ULOutSocket(self, self.get_property)

    def get_property(self):
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        props = (
            [p[0] for p in game_object.blenderObject.items()]
            if self.mode else
            game_object.getPropertyNames()
        )
        if property_name in props:
            obj = game_object if self.mode in [0, 'GAME'] else game_object.blenderObject
            return obj.get(property_name)
        game_object[property_name] = None

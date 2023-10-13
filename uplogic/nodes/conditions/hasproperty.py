from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULHasProperty(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.game_object = None
        self.property_name = None
        self.mode = 0
        self.OUT = ULOutSocket(self, self.get_stat)

    def get_stat(self):
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        return (
            property_name in [p[0] for p in game_object.blenderObject.items()]
            if self.mode else
            property_name in game_object.getPropertyNames()
        )

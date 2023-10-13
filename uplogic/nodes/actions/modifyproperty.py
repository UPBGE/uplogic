from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULModifyProperty(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.property_name = None
        self.property_value = None
        self.operator = None
        self.mode = 0
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        property_value = self.get_input(self.property_value)
        obj = game_object.blenderObject if self.mode else game_object
        value = obj.get(property_name, 0)
        obj[property_name] = (
            self.operator(value, property_value)
        )
        self.done = True

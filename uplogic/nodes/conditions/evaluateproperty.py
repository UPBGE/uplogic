from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULConditionNode


class ULEvaluateProperty(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.game_object = None
        self.property_name = None
        self.operator = None
        self.mode = 0
        self.compare_value = None
        self.OUT = ULOutSocket(self, self.get_out)
        self.val = 0
        self.VAL = ULOutSocket(self, self.get_val)

    def get_out(self):
        compare_value = self.get_input(self.compare_value)
        return self.operator(self.val, compare_value)

    def get_val(self):
        return self.val

    def evaluate(self):
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        obj = game_object if self.mode in [0, 'GAME'] else game_object.blenderObject
        self.val = obj.get(property_name)

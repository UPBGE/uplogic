from uplogic.nodes import ULActionNode
from uplogic.utils.math import clamp


class ULModifyProperty(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.property_name = None
        self.property_value = None
        self.operator = None
        self.mode = 0
        self.clamp = False
        self.min_value = 0.0
        self.max_value = 1.0
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        property_value = self.get_input(self.property_value)
        obj = game_object.blenderObject if self.mode else game_object
        value = obj.get(property_name, 0)
        result = self.operator(value, property_value)
        if self.clamp:
            result = clamp(
                result,
                self.get_input(self.min_value),
                self.get_input(self.max_value)
            )
        obj[property_name] = result
        if self.mode:
            obj.color = obj.color
        self._done = True

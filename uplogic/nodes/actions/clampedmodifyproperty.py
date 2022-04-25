from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting
from uplogic.utils import not_met
from uplogic.utils import clamp


class ULClampedModifyProperty(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.property_name = None
        self.property_value = None
        self.mode = 'GAME'
        self.operator = None
        self.range = None
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        game_object = self.get_input(self.game_object)
        if not_met(condition):
            return
        if is_invalid(game_object):
            return
        property_name = self.get_input(self.property_name)
        property_value = self.get_input(self.property_value)
        val_range = self.get_input(self.range)
        if is_waiting(property_name, property_value):
            return
        self._set_ready()
        obj = game_object if self.mode == 'GAME' else game_object.blenderObject
        value = obj.get(property_name, 0)
        new_val = self.operator(value, property_value)
        obj[property_name] = (
            clamp(new_val, val_range.x, val_range.y)
        )
        self.done = True

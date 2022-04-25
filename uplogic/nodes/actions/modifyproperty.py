from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting
from uplogic.utils import not_met


class ULModifyProperty(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.property_name = None
        self.property_value = None
        self.operator = None
        self.mode = 'GAME'
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        property_value = self.get_input(self.property_value)
        if is_waiting(property_name, property_value):
            return
        if is_invalid(game_object):
            return
        self._set_ready()
        obj = game_object if self.mode == 'GAME' else game_object.blenderObject
        value = obj.get(property_name, 0)
        obj[property_name] = (
            self.operator(value, property_value)
        )
        self.done = True

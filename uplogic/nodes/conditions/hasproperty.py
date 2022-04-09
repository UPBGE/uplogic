from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_WAITING
from uplogic.utils import is_invalid


class ULHasProperty(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.game_object = None
        self.property_name = None
        self.mode = 'GAME'
        self.OUT = ULOutSocket(self, self.get_stat)

    def get_stat(self):
        socket = self.get_output('result')
        if socket is None:
            game_object = self.get_input(self.game_object)
            property_name = self.get_input(self.property_name)
            if is_invalid(game_object, property_name):
                return STATUS_WAITING
            return self.set_output(
                'stat',
                (
                    property_name in game_object.getPropertyNames()
                )
            ) if self.mode == 'GAME' else self.set_output(
                'stat',
                (
                    property_name in [p[0] for p in game_object.blenderObject.items()]
                )
            )
        return socket

    def evaluate(self):
        self._set_ready()

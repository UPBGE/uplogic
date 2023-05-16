from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils.constants import STATUS_WAITING
from uplogic.utils import is_invalid
import bge


class ULGetObject(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = ULOutSocket(self, self.get_obj)
        self.scene = bge.logic.getCurrentScene()

    def get_obj(self):
        game_object = self.get_input(self.game_object)
        if is_invalid(game_object):
            return STATUS_WAITING
        if isinstance(game_object, str):
            game_object = self.scene.objects[game_object]
        return game_object

    def evaluate(self):
        self._set_ready()

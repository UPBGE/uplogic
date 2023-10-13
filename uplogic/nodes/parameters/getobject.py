from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
import bge


class ULGetObject(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = ULOutSocket(self, self.get_obj)
        self.scene = bge.logic.getCurrentScene()

    def get_obj(self):
        return self.get_input(self.game_object)

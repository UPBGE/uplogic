from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import world_to_screen


class ULScreenPosition(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.camera = None
        self.pos = None
        self.OUT = ULOutSocket(self, self.get_pos)

    def get_pos(self):
        game_object = self.get_input(self.game_object)
        return world_to_screen(game_object)


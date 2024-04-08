from uplogic.nodes import ULParameterNode


class GetCollisionGroupNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.mode = 0
        self.INT = self.add_output(self.get_int)

    def get_int(self):
        game_object = self.get_input(self.game_object)
        return game_object.collisionMask if self.mode else game_object.collisionGroup

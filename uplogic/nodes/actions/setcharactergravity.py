from bge import constraints
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetCharacterGravity(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.gravity = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        gravity = self.get_input(self.gravity)
        physics = constraints.getCharacter(game_object)
        if physics:
            physics.gravity = gravity
        else:
            game_object.gravity = gravity
        self.done = True

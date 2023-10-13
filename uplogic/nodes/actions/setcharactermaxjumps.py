from bge import constraints
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetCharacterMaxJumps(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.max_jumps = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        max_jumps = self.get_input(self.max_jumps)
        physics = constraints.getCharacter(game_object)
        physics.maxJumps = max_jumps
        self.done = True

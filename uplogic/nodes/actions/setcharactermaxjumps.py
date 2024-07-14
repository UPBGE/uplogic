from bge import constraints
from uplogic.nodes import ULActionNode


class ULSetCharacterMaxJumps(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.max_jumps = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        max_jumps = self.get_input(self.max_jumps)
        physics = constraints.getCharacter(game_object)
        physics.maxJumps = max_jumps
        self._done = True

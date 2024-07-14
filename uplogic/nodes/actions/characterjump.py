from bge import constraints
from uplogic.nodes import ULActionNode


class ULCharacterJump(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        physics = constraints.getCharacter(game_object)
        physics.jump()

        self._done = True

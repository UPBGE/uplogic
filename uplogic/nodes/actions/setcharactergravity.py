from bge import constraints
from uplogic.nodes import ULActionNode


class ULSetCharacterGravity(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.gravity = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        gravity = self.get_input(self.gravity)
        physics = constraints.getCharacter(game_object)
        if physics:
            physics.gravity = gravity
        else:
            game_object.gravity = gravity
        self._done = True

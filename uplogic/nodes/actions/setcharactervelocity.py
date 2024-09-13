from bge import constraints
from uplogic.nodes import ULActionNode


class ULSetCharacterVelocity(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.vel = None
        self.time = None
        self.local = False
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        local = self.local
        physics = constraints.getCharacter(game_object)
        vel = self.get_input(self.vel)
        time = self.get_input(self.time)
        physics.setVelocity(vel, time, local)
        self._done = True

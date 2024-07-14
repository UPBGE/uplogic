from uplogic.nodes import ULActionNode


class ULApplyImpulse(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.point = None
        self.impulse = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        point = self.get_input(self.point)
        impulse = self.get_input(self.impulse)
        local = self.local
        if impulse:
            game_object.applyImpulse(point, impulse, local)
        self._done = True

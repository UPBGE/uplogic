from uplogic.nodes import ULActionNode


class ULApplyMovement(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.movement = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        movement = self.get_input(self.movement)
        local = self.local
        if movement:
            game_object.applyMovement(movement, local)
        self._done = True

from uplogic.nodes import ULActionNode


class ULSetCollisionMask(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.slots = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        slots = self.get_input(self.slots)
        game_object.collisionMask = slots

        self._done = True

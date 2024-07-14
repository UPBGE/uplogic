from uplogic.nodes import ULActionNode


class ULSetCollisionGroup(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.slots = None
        self.mode = 0
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        slots = self.get_input(self.slots)
        if self.mode:
            game_object.collisionMask = slots
        else:
            game_object.collisionGroup = slots
        self._done = True

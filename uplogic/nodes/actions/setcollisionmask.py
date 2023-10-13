from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetCollisionMask(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.slots = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        slots = self.get_input(self.slots)
        game_object.collisionMask = slots

        self.done = True

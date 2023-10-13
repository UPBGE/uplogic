from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULApplyMovement(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.movement = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        movement = self.get_input(self.movement)
        local = self.local
        if movement:
            game_object.applyMovement(movement, local)
        self.done = True

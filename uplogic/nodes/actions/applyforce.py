from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULApplyForce(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.force = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        force = self.get_input(self.force)
        local = self.local
        game_object.applyForce(force, local)
        self.done = True

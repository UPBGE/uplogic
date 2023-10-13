from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetPhysics(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.activate = False
        self.free_const = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        activate = self.get_input(self.activate)
        free_const = self.get_input(self.free_const)
        if activate:
            game_object.restorePhysics()
        else:
            game_object.suspendPhysics(free_const)
        self.done = True

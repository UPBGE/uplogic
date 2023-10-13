from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetDynamics(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.activate = False
        self.ghost = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        ghost = self.get_input(self.ghost)
        activate = self.get_input(self.activate)
        if activate:
            game_object.restoreDynamics()
        else:
            game_object.suspendDynamics(ghost)
        self.done = True

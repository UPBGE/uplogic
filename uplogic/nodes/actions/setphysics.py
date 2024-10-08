from uplogic.nodes import ULActionNode


class ULSetPhysics(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.activate = False
        self.free_const = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        activate = self.get_input(self.activate)
        free_const = self.get_input(self.free_const)
        if activate:
            game_object.restorePhysics()
        else:
            game_object.suspendPhysics(free_const)
        self._done = True

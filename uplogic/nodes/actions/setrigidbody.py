from uplogic.nodes import ULActionNode


class ULSetRigidBody(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.activate = False
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        activate = self.get_input(self.activate)
        if activate:
            game_object.enableRigidBody()
        else:
            game_object.disableRigidBody()
        self._done = True

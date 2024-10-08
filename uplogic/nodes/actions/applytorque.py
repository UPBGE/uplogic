from uplogic.nodes import ULActionNode


class ULApplyTorque(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.torque = None
        self.local = False
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        torque = self.get_input(self.torque)
        local = self.local
        if torque:
            game_object.applyTorque(torque, local)
        self._done = True

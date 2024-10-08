from uplogic.nodes import ULActionNode


class ULApplyRotation(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.rotation = None
        self.local = False
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        rotation = self.get_input(self.rotation)
        local = self.local
        if rotation:
            if len(rotation) == 3:
                game_object.applyRotation(rotation, local)
            else:
                game_object.applyRotation(rotation.to_euler("XYZ"), local)
        self._done = True

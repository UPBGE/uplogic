from uplogic.nodes import ULActionNode


class ULAlignAxisToVector(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.vector = None
        self.axis = None
        self.factor = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        v = self.get_input(self.vector).copy()
        axis = self.get_input(self.axis)
        factor = self.get_input(self.factor)
        if not self.local:
            v -= game_object.worldPosition
        if axis > 2:
            v.negate()
            axis -= 3
        game_object.alignAxisToVect(v, axis, factor)
        self._done = True

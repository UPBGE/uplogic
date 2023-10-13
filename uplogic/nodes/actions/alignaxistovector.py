from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULAlignAxisToVector(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.vector = None
        self.axis = None
        self.factor = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        v = self.get_input(self.vector)
        axis = self.get_input(self.axis)
        factor = self.get_input(self.factor)
        if not self.local:
            v -= game_object.worldPosition
        if axis > 2:
            matvec = v.copy()
            matvec.negate()
            v = matvec
            axis -= 3
        game_object.alignAxisToVect(v, axis, factor)
        self.done = True

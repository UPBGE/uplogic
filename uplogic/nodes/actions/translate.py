from uplogic.nodes import ULActionNode, ULOutSocket


class ULTranslate(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.moving_object = None
        self.local = None
        self.vect = None
        self.speed = None
        self._t = None
        self._old_values = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        print('"Translate" node is deprecated!')

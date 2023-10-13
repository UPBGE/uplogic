from uplogic.nodes import ULActionNode, ULOutSocket


class ULStopSound(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.sound = None
        self.done = False
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        sound = self.get_input(self.sound)
        sound.stop()
        self.done = True

from uplogic.nodes import ULActionNode


class ULStopSound(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.sound = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        sound = self.get_input(self.sound)
        sound.stop()
        self._done = True

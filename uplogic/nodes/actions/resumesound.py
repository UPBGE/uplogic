from uplogic.nodes import ULActionNode


class ULResumeSound(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.sound = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        sound = self.get_input(self.sound)
        sound.resume()
        self._done = True

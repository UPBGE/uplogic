from uplogic.nodes import ULActionNode
from uplogic.audio.sound import ULSound


class ULPauseSound(ULActionNode):
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
        sound: ULSound = self.get_input(self.sound)
        sound.pause()
        self._done = True

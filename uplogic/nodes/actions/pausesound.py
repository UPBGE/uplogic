from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.audio.sound import ULSound


class ULPauseSound(ULActionNode):
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
        sound: ULSound = self.get_input(self.sound)
        sound.pause()
        self.done = True

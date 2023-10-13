from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.data import GlobalDB


class ULStopAllSounds(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.done = False
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        aud_sys = GlobalDB.retrieve('uplogic.audio').get('default')
        aud_sys.device.stopAll()
        self.done = True

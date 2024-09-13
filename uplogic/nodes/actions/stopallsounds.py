from uplogic.nodes import ULActionNode
from uplogic.data import GlobalDB


class ULStopAllSounds(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        aud_sys = GlobalDB.retrieve('uplogic.audio').get('default')
        aud_sys.device.stopAll()
        self._done = True

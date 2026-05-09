from uplogic.nodes import ULActionNode
from uplogic.audio.fmod import FMod


class FModStartEventNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.event = ''
        self.source = ''
        self.channel = 'default'
        self.mask = 65535
        self._evt = None
        self.OUT = self.add_output(self.get_done)
        self.EVT = self.add_output(self.get_evt)

    def get_done(self):
        return self._done

    def get_evt(self):
        return self._evt

    def evaluate(self):
        if not self.get_condition():
            return
        self._evt = FMod.event(
            f'event:/{self.get_input(self.event)}',
            self.get_input(self.source),
            self.get_input(self.channel)
        )
        self._evt.occlusion_mask = self.mask
        self._done = True

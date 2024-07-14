from uplogic.nodes import ULActionNode
from uplogic.audio.fmod import FMod


class FModLoadBankNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.path = ''
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        FMod.load_bank(self.get_input(self.path))
        self._done = True

from uplogic.nodes import ULActionNode
from uplogic.audio.fmod import FMod
import os


class FModLoadBankNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.load_master = False
        self.load_strings = False
        self.path = ''
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        path = self.get_input(self.path)
        if self.load_master:
            ppath = os.path.join(*os.path.split(path)[:-1])
            FMod.load_bank(os.path.join(ppath, 'Master.bank'))
            if self.load_strings:
                FMod.load_bank(os.path.join(ppath, 'Master.strings.bank'))
        FMod.load_bank(self.get_input(self.path))
        self._done = True

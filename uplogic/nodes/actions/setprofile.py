from bge import render
from uplogic.nodes import ULActionNode


class ULSetProfile(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.use_profile = None
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        use_profile = self.get_input(self.use_profile)
        render.showProfile(use_profile)
        self.done = True

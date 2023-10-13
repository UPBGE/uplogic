from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULLoadBlendFile(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.file_name = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        file_name = self.get_input(self.file_name)
        logic.startGame(file_name)
        self.done = True

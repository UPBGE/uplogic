from bge import logic
from uplogic.nodes import ULActionNode


class ULLoadBlendFile(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.file_name = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        file_name = self.get_input(self.file_name)
        logic.startGame(file_name)
        self._done = True

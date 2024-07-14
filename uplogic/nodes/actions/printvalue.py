from uplogic.nodes import ULActionNode
from uplogic.console import write


class ULPrintValue(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.value = None
        self.msg_type = 'INFO'
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        value = self.get_input(self.value)
        write(value, self.msg_type)
        self._done = True

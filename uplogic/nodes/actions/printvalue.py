from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.logging import log


class ULPrintValue(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.value = None
        self.done = None
        self.msg_type = 'INFO'
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        value = self.get_input(self.value)
        log(value, self.msg_type)
        self.done = True

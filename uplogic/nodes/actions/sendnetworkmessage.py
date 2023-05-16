from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils import is_waiting
from uplogic.utils import not_met


class ULSendNetworkMessage(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.entity = None
        self.data = None
        self.subject = None
        self._done = False
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        self._done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            self._set_ready()
            return
        entity = self.get_input(self.entity)
        if entity:
            entity.send(self.get_input(self.data), self.get_input(self.subject))
        self._done = True

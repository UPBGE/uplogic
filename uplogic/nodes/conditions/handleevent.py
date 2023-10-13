from uplogic.events import receive
from uplogic.events import ULEvent
from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULHandleEvent(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.subject = None
        self.event = None
        self.OUT = ULOutSocket(self, self.get_received)
        self.BODY = ULOutSocket(self, self.get_body)
        self.TARGET = ULOutSocket(self, self.get_target)

    def get_received(self):
        return isinstance(self.event, ULEvent)

    def get_body(self):
        return self.event.content if self.event else None

    def get_target(self):
        return self.event.messenger if self.event else None

    def evaluate(self):
        subject = self.get_input(self.subject)
        self.event = receive(subject)

from uplogic.events import receive
from uplogic.events import Event
from uplogic.nodes import ULConditionNode


class ULHandleEvent(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.subject = None
        self.event = None
        self.target = None
        self.OUT = self.add_output(self.get_received)
        self.BODY = self.add_output(self.get_body)
        self.TARGET = self.add_output(self.get_target)

    def get_received(self):
        return isinstance(self.event, Event)

    def get_body(self):
        return self.event.content if self.event else None

    def get_target(self):
        return self.event.messenger if self.event else None

    def evaluate(self):
        target = self.get_input(self.target)
        self.event = receive(self.get_input(self.subject), target if target else self.network.owner)

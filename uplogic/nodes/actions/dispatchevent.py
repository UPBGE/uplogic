from uplogic.events import send
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULDispatchEvent(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.subject = None
        self.body = None
        self.target = None
        self.old_subject = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        subject = self.get_input(self.subject)
        body = self.get_input(self.body)
        target = self.get_input(self.target)
        send(subject, body, target)
        self.done = True

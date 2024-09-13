from uplogic.events import send
from uplogic.nodes import ULActionNode


class ULDispatchEvent(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.subject = None
        self.body = None
        self.target = None
        self.old_subject = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        subject = self.get_input(self.subject)
        body = self.get_input(self.body)
        target = self.get_input(self.target)
        send(subject, body, target)
        self._done = True

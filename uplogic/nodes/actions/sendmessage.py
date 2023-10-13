from uplogic.nodes import ULActionNode
from bge.types import KX_GameObject
from bge.logic import sendMessage
from uplogic.nodes import ULOutSocket


class ULSendMessage(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.from_obj = None
        self.to_obj = None
        self.subject = None
        self.body = None
        self.done = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        from_obj: KX_GameObject = self.get_input(self.from_obj)
        to_obj: KX_GameObject = self.get_input(self.to_obj)
        subject = self.get_input(self.subject)
        body = self.get_input(self.body)
        sendMessage(
            subject,
            body,
            to_obj.name if to_obj else '',
            from_obj.name if from_obj else ''
        )
        self.done = True

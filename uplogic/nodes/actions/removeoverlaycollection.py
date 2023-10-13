from bge import logic
from uplogic.nodes import ULActionNode, ULOutSocket


class ULRemoveOverlayCollection(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.collection = None
        self.done = False
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        logic.getCurrentScene().removeOverlayCollection(
            self.get_input(self.collection)
        )
        self.done = True

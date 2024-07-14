from bge import logic
from uplogic.nodes import ULActionNode


class ULRemoveOverlayCollection(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.collection = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        logic.getCurrentScene().removeOverlayCollection(
            self.get_input(self.collection)
        )
        self._done = True

from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULActionNode
from uplogic.utils import is_waiting
from uplogic.utils import not_met
from bge import logic


class ULSetScene(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        scene = self.get_input(self.scene)
        if is_waiting(scene):
            return
        self._set_ready()
        logic.getCurrentScene().replace(scene)
        self.done = True

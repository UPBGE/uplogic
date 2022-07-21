from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.utils import not_met
from uplogic import get_mainloop


class ULEndGame(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None

    def evaluate(self):
        self._set_ready()
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        mainloop = get_mainloop()
        if mainloop:
            mainloop.stop()
        logic.endGame()

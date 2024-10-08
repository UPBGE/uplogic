from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.loop import get_mainloop


class ULEndGame(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None

    def evaluate(self):
        if not self.get_condition():
            return
        mainloop = get_mainloop()
        if mainloop:
            mainloop.stop()
        logic.endGame()

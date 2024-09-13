from uplogic.nodes import ULConditionNode
from uplogic.nodes import LoopList


class LoopNode(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = False
        self.get_input = self._get_input
        self.items = []
        self.LOOP = self.add_output(self.get_loop)
        self.LIST = self.add_output(self.get_list)

    @property
    def loop_mode(self):
        return self._loop_mode

    @loop_mode.setter
    def loop_mode(self, val):
        self._loop_mode = False

    def get_loop(self):
        cond = self.get_input(self.condition)
        return LoopList([cond for x in self.get_input(self.items)])

    def get_list(self):
        return LoopList([self.get_input(item) for item in self.get_input(self.items)])

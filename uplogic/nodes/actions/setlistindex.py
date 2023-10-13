from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetListIndex(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.items: list = None
        self.index: int = None
        self.val = None
        self.new_list: list = None
        self.done: bool = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.LIST = ULOutSocket(self, self.get_list)

    def get_done(self):
        return self.done

    def get_list(self):
        return self.new_list

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        list_d: list = self.get_input(self.items)
        index: int = self.get_input(self.index)
        val = self.get_input(self.val)
        list_d[index] = val
        self.new_list = list_d
        self.done = True

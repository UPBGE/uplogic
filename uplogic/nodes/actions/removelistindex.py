from uplogic.nodes import ULActionNode
from uplogic.utils import debug

class ULRemoveListIndex(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.items = None
        self.idx = None
        self.new_list = None
        self.OUT = self.add_output(self.get_done)
        self.LIST = self.add_output(self.get_list)

    def get_done(self):
        return self._done

    def get_list(self):
        return self.new_list

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        list_d = self.get_input(self.items)
        idx = self.get_input(self.idx)
        if len(list_d) > idx:
            del list_d[idx]
        else:
            debug("List Index exceeds length!")
            return
        self.new_list = list_d
        self._done = True

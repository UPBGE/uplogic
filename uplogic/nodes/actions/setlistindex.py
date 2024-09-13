from uplogic.nodes import ULActionNode


class ULSetListIndex(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.items: list = None
        self.index: int = None
        self.val = None
        self.new_list: list = None
        self.OUT = self.add_output(self.get_done)
        self.LIST = self.add_output(self.get_list)

    def get_done(self):
        return self._done

    def get_list(self):
        return self.new_list

    def evaluate(self):
        if not self.get_condition():
            return
        list_d: list = self.get_input(self.items)
        index: int = self.get_input(self.index)
        val = self.get_input(self.val)
        list_d[index] = val
        self.new_list = list_d
        self._done = True

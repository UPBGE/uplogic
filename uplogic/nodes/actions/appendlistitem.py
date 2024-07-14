from uplogic.nodes import ULActionNode


class ULAppendListItem(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.items: list = None
        self.val = None
        self.new_list: list = None
        self._done: bool = None
        self.OUT = self.add_output(self.get_done)
        self.LIST = self.add_output(self.get_list)

    def get_done(self):
        return self._done

    def get_list(self):
        return self.new_list

    def evaluate(self):
        self._done: bool = False
        if not self.get_input(self.condition):
            return
        list_d: list = self.get_input(self.items)
        val = self.get_input(self.val)
        list_d.append(val)
        self.new_list = list_d
        self._done = True

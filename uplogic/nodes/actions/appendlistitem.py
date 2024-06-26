from uplogic.nodes import ULActionNode


class ULAppendListItem(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.items: list = None
        self.val = None
        self.new_list: list = None
        self.done: bool = None
        self.OUT = self.add_output(self.get_done)
        self.LIST = self.add_output(self.get_list)

    def get_done(self):
        return self.done

    def get_list(self):
        return self.new_list

    def evaluate(self):
        self.done: bool = False
        if not self.get_input(self.condition):
            return
        list_d: list = self.get_input(self.items)
        val = self.get_input(self.val)
        list_d.append(val)
        self.new_list = list_d
        self.done = True

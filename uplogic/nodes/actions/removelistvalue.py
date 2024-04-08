from uplogic.nodes import ULActionNode
from uplogic.utils import debug


class ULRemoveListValue(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.items = None
        self.val = None
        self.new_list = None
        self.done = None
        self.OUT = self.add_output(self.get_done)
        self.LIST = self.add_output(self.get_list)

    def get_done(self):
        return self.done

    def get_list(self):
        return self.new_list

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        list_d = self.get_input(self.items)
        val = self.get_input(self.val)
        if val in list_d:
            list_d.remove(val)
        else:
            debug("List Remove Value Node: Item '{}' not in List!".format(val))
            return
        self.new_list = list_d
        self.done = True

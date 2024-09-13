from uplogic.nodes import ULParameterNode
from uplogic.nodes import LoopList


class ULListFromItems(ULParameterNode):
    # XXX: Deprecated
    def __init__(self):
        ULParameterNode.__init__(self)
        self.items: list = None
        self.LIST = self.add_output(self.get_list)

    def get_list(self):
        return [self.get_input(item) for item in self.items]


class ListFromItemsNode(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.items = []
        self.LIST = self.add_output(self.get_list)

    def get_list(self):
        li = [self.get_input(item) for item in self.get_input(self.items)]
        return LoopList(li) if self.loop_mode else li

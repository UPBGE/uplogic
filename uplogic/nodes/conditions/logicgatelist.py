from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULConditionNode


class ULLogicGateList(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.items = None
        self.list: list = None
        self.OUT = ULOutSocket(self, self.get_and_list)

        self.getters = [
            self.get_and_list,
            self.get_or_list
        ]

        self.gate = 0

    @property
    def gate(self):
        return None

    @gate.setter
    def gate(self, val):
        self.OUT.get_value = self.getters[val]

    def get_and_list(self):
        for item in self.items:
            it = self.get_input(item)
            if not it:
                return False
        return True

    def get_or_list(self):
        for item in self.items:
            it = self.get_input(item)
            if it is True:
                return True
        return False

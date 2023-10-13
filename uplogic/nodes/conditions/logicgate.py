from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULLogicGate(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = None
        self.cb = None
        self.OUT = ULOutSocket(self, self.get_and)

        self.getters = [
            self.get_and,
            self.get_or,
            self.get_xor,
            self.get_not,
            self.get_nand,
            self.get_nor,
            self.get_xnor,
            self.get_and_not
        ]
        self.gate = 0

    @property
    def gate(self):
        return None

    @gate.setter
    def gate(self, val):
        self.OUT.get_value = self.getters[val]

    def get_and(self):
        ca = self.get_input(self.ca)
        return ca and self.get_input(self.cb)

    def get_or(self):
        ca = self.get_input(self.ca)
        cb = self.get_input(self.cb)
        return ca or cb

    def get_xor(self):
        ca = self.get_input(self.ca)
        cb = self.get_input(self.cb)
        return (ca or cb) and not (ca and cb)

    def get_not(self):
        condition = self.get_input(self.ca)
        return not condition

    def get_nand(self):
        ca = self.get_input(self.ca)
        cb = self.get_input(self.cb)
        return not (ca and cb)

    def get_nor(self):
        ca = self.get_input(self.ca)
        cb = self.get_input(self.cb)
        return not (ca or cb)

    def get_xnor(self):
        ca = self.get_input(self.ca)
        cb = self.get_input(self.cb)
        return not (ca or cb) or (ca and cb)

    def get_and_not(self):
        ca = self.get_input(self.ca)
        cb = self.get_input(self.cb)
        return ca and not cb

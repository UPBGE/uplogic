from uplogic.nodes import ULConditionNode, ULOutSocket


class ULAnd(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = None
        self.cb = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        ca = self.get_input(self.ca)
        return ca and self.get_input(self.cb)


class ULAndList(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = True
        self.cb = True
        self.cc = True
        self.cd = True
        self.ce = True
        self.cf = True
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        results = [
            self.get_input(self.ca),
            self.get_input(self.ca),
            self.get_input(self.ca),
            self.get_input(self.ca),
            self.get_input(self.ca),
            self.get_input(self.ca)
        ]
        return False not in results

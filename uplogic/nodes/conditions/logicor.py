from uplogic.nodes import ULConditionNode, ULOutSocket


class ULOr(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = False
        self.cb = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return (
            self.get_input(self.ca)
            or
            self.get_input(self.cb)
        )


class ULOrList(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = False
        self.cb = False
        self.cc = False
        self.cd = False
        self.ce = False
        self.cf = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        conds = [
            self.get_input(self.ca),
            self.get_input(self.cb),
            self.get_input(self.cc),
            self.get_input(self.cd),
            self.get_input(self.ce),
            self.get_input(self.cf)
        ]
        return True in conds

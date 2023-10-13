from uplogic.nodes import ULActionNode, ULOutSocket


class ULSetPyInstanceAttr(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.instance = None
        self.attr = None
        self.value = None
        self.done = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        instance = self.get_input(self.instance)
        attr = self.get_input(self.attr)
        value = self.get_input(self.value)
        setattr(instance, attr, value)
        self.done = True

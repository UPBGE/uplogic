from uplogic.nodes import ULActionNode


class ULSetPyInstanceAttr(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.instance = None
        self.attr = None
        self.value = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        instance = self.get_input(self.instance)
        attr = self.get_input(self.attr)
        value = self.get_input(self.value)
        setattr(instance, attr, value)
        self._done = True

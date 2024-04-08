from uplogic.nodes import ULParameterNode


class ULGetPyInstanceAttr(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.instance = None
        self.attr = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        instance = self.get_input(self.instance)
        attr = self.get_input(self.attr)
        return getattr(instance, attr, None)

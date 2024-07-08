from uplogic.nodes import ULActionNode


class ULRemoveParent(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.child_object = None
        self.done = None
        self._parent = None
        self.OUT = self.add_output(self.get_done)
        self.PARENT = self.add_output(self.get_parent)

    def get_done(self):
        return self.done

    def get_parent(self):
        return self._parent

    def reset(self):
        super().reset()
        self._parent = None

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        child_object = self.get_input(self.child_object)
        self._parent = child_object.parent
        child_object.removeParent()
        self.done = True

from uplogic.nodes import ULActionNode


class ULSetParent(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.child_object = None
        self.parent_object = None
        self.compound = True
        self.ghost = True
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        child_object = self.get_input(self.child_object)
        parent_object = self.get_input(self.parent_object)
        compound = self.get_input(self.compound)
        ghost = self.get_input(self.ghost)
        child_object.setParent(parent_object, compound, ghost)
        self._done = True

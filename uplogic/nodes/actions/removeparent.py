from uplogic.nodes import ULActionNode


class ULRemoveParent(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.child_object = None
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        child_object = self.get_input(self.child_object)
        child_object.removeParent()
        self.done = True

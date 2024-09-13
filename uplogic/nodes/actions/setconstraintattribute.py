from uplogic.nodes import ULActionNode


class SetConstraintAttributeNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.object = None
        self.constraint = None
        self.attribute = None
        self.value = None
        self._done: bool = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        consts = self.get_input(self.object).blenderObject.constraints
        const = consts[self.get_input(self.constraint)]
        setattr(
            const,
            self.get_input(self.attribute),
            self.get_input(self.value)
        )
        self._done = True

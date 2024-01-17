from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class SetConstraintAttributeNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.object = None
        self.constraint = None
        self.attribute = None
        self.value = None
        self.done: bool = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        consts = self.get_input(self.object).blenderObject.constraints
        const = consts[self.get_input(self.constraint)]
        setattr(
            const,
            self.get_input(self.attribute),
            self.get_input(self.value)
        )
        self.done = True

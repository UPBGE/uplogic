from uplogic.nodes import ULParameterNode


class ULGetCollection(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.collection = None
        self.OUT = self.add_output(self.get_collection)

    def get_collection(self):
        return self.get_input(self.collection)

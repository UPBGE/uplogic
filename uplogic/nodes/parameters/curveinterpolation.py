from uplogic.nodes import ULParameterNode


class CurveInterpolationNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.mapping = None
        self.OUT = self.add_output(self.get_result)

    def get_result(self):
        val = self.get_input(self.value)
        mapping = self.mapping.curve

        return mapping.evaluate(mapping.curves[0], val)

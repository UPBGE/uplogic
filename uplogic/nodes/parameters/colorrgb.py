from uplogic.nodes import ULParameterNode


class ULColorRGB(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.color = None
        self.output_vector = None
        self.OUTV = self.add_output(self.get_out_v)

    def get_out_v(self):
        c = self.get_input(self.color)
        c = c.copy()
        c.resize_3d()
        return c

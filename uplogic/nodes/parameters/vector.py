from mathutils import Vector
from uplogic.nodes import ULParameterNode


class VectorNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.vector = Vector()
        self.OUT = self.add_output(self.get_vec)

    def get_vec(self):
        return self.vector

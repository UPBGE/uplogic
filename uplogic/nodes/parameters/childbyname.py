from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from bge.types import KX_GameObject


class ULChildByName(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.from_parent = None
        self.child = None
        self.CHILD = ULOutSocket(self, self.get_child)

    def get_child(self):
        parent: KX_GameObject = self.get_input(self.from_parent)
        child: KX_GameObject = self.get_input(self.child)
        return parent.childrenRecursive.get(child.name)

    def evaluate(self):
        pass

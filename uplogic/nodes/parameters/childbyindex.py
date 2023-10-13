from bge.types import KX_GameObject as GameObject
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULChildByIndex(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.from_parent: GameObject = None
        self.index: int = None
        self.CHILD = ULOutSocket(self, self.get_child)

    def get_child(self):
        parent: GameObject = self.get_input(self.from_parent)
        index: int = self.get_input(self.index)
        if len(parent.children) > index:
            return parent.children[index]

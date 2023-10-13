from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from bpy.types import NodeTree


class ULGetNodeAttribute(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.mat_name = None
        self.node_name = None
        self.internal = None
        self.attribute = None
        self.OUT = ULOutSocket(self, self._get_val)

    def _get_val(self):
        tree: NodeTree = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        internal = self.get_input(self.internal)
        attribute = self.get_input(self.attribute)
        target = (
            tree
            .nodes[node_name]
        )
        if internal:
            target = getattr(target, internal, target)
        return getattr(target, attribute, None)

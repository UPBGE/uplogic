from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from bpy.types import NodeTree


class ULGetNodeSocket(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.tree_name = None
        self.node_name = None
        self.input_slot = None
        self.OUT = ULOutSocket(self, self._get_val)

    def _get_val(self):
        tree: NodeTree = self.get_input(self.tree_name)
        node_name = self.get_input(self.node_name)
        input_slot = self.get_input(self.input_slot)
        return (
            tree
            .nodes[node_name]
            .inputs[input_slot]
            .default_value
        )

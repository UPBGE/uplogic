from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from bpy.types import Material
import bpy


class ULGetMaterialNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.mat_name = None
        self.node_name = None
        self.OUT = ULOutSocket(self, self._get_val)

    def _get_val(self):
        material: Material = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        return (
            material
            .node_tree
            .nodes[node_name]
        )

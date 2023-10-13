from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from bpy.types import Material
import bpy


class ULGetMaterialAttribute(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.mat_name = None
        self.node_name = None
        self.internal = None
        self.attribute = None
        self.OUT = ULOutSocket(self, self._get_val)

    def _get_val(self):
        material: Material = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        internal = self.get_input(self.internal)
        attribute = self.get_input(self.attribute)
        target = (
            material
            .node_tree
            .nodes[node_name]
        )
        if internal:
            target = getattr(target, internal, target)
        return getattr(target, attribute, None)

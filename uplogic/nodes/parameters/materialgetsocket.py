from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from bpy.types import Material


class ULGetMaterialSocket(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.mat_name = None
        self.node_name = None
        self.input_slot = None
        self.OUT = ULOutSocket(self, self._get_val)

    def _get_val(self):
        material: Material = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        input_slot = self.get_input(self.input_slot)
        return (
            material
            .node_tree
            .nodes[node_name]
            .inputs[input_slot]
            .default_value
        )

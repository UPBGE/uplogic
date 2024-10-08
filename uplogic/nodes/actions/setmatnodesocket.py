from uplogic.nodes import ULActionNode
from bpy.types import Material


class ULSetMatNodeSocket(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.mat_name = None
        self.node_name = None
        self.input_slot = None
        self.value = None
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        material: Material = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        input_slot = self.get_input(self.input_slot)
        value = self.get_input(self.value)
        (
            material
            .node_tree
            .nodes[node_name]
            .inputs[input_slot]
            .default_value
        ) = value
        self._done = True

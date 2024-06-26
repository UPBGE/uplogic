from uplogic.nodes import ULActionNode
from bpy.types import NodeTree


class ULSetNodeSocket(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.tree_name = None
        self.node_name = None
        self.input_slot = None
        self.value = None
        self.done = False
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        tree: NodeTree = self.get_input(self.tree_name)
        node_name = self.get_input(self.node_name)
        input_slot = self.get_input(self.input_slot)
        value = self.get_input(self.value)
        (
            tree
            .nodes[node_name]
            .inputs[input_slot]
            .default_value
        ) = value
        self.done = True

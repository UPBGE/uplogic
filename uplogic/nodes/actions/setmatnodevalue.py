from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bpy.types import Material
import bpy


class ULSetMatNodeValue(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.mat_name = None
        self.node_name = None
        self.internal = None
        self.attribute = None
        self.value = None
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        material: Material = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        attribute = self.get_input(self.attribute)
        internal = self.get_input(self.internal)
        value = self.get_input(self.value)
        target = (
            material
            .node_tree
            .nodes[node_name]
        )
        if internal:
            target = getattr(target, internal, target)
        if hasattr(target, attribute):
            setattr(target, attribute, value)
        self.done = True

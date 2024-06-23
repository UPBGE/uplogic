from uplogic.nodes import ULParameterNode
from os import path, pardir
from ...console import error
import bpy


class JoinPathNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.items = []
        self.PATH = self.add_output(self._get_path)

    def _get_path(self):
        get_ipt = self.get_input
        items = get_ipt(self.items)
        items = [get_ipt(item) for item in self.items]
        return path.join(*items)


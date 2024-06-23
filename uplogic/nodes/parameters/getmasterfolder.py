from uplogic.nodes import ULParameterNode
from os import path, pardir
from ...console import error
import bpy


class GetMasterFolderNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.name = ''
        self.PATH = self.add_output(self._get_path)

    def _get_path(self):
        name = self.get_input(self.name)

        parent_dir = path.join(bpy.path.abspath('//'))[:-1]
        while not parent_dir.endswith(name):
            pdir = path.abspath(path.join(parent_dir, pardir))
            if pdir == parent_dir:
                error("Can't go beyond drive's root!")
                return ''
            parent_dir = pdir
        return parent_dir

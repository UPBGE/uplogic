from uplogic.nodes import ULParameterNode
from uplogic.utils import get_master_folder
import bpy


class GetMasterFolderNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.name = ''
        self.PATH = self.add_output(self._get_path)

    def _get_path(self):
        name = self.get_input(self.name)

        return get_master_folder(name)

from uplogic.nodes import ULParameterNode
from uplogic.utils import debug
import bpy
import json
import os


class ULLoadVariableDict(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.file_name = None
        self.path = ''
        self.VAR = self.add_output(self.get_var)

    def get_var(self):
        path = self.get_input(self.path)

        path = (bpy.path.abspath(path))
        os.makedirs(path, exist_ok=True)

        return self.read_from_json(path)

    def read_from_json(self, path):
        if not path.endswith('.json'):
            path = os.path.join(path, f'{self.get_input(self.file_name)}.json')
        if not os.path.isfile(path):
            debug('No Saved Variables!')
            return
        f = open(path, 'r')
        data = json.load(f)
        f.close()
        return data

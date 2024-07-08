from uplogic.nodes import ULParameterNode
from uplogic.utils import debug
import bpy
import json
import os


class ULLoadVariable(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.name = None
        self.default_value = None
        self.file_name = None
        self.path = ''
        self.VAR = self.add_output(self.get_var)

    def get_var(self):
        name = self.get_input(self.name)
        path = self.get_input(self.path)
        path = (bpy.path.abspath(path))

        os.makedirs(path, exist_ok=True)

        return self.read_from_json(path, name)

    def read_from_json(self, path, name):
        if not path.endswith('.json'):
            path = os.path.join(path, f'{self.get_input(self.file_name)}.json')
        if os.path.isfile(path):
            f = open(path, 'r')
            data = json.load(f)
            if name not in data:
                debug(f'"{name}" is not a saved Variabe!')
                return self.get_input(self.default_value)
            f.close()
            return data.get(name)
        else:
            debug('No saved variables!')
            return self.get_input(self.default_value)



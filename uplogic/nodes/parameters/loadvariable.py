from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
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
        self.VAR = ULOutSocket(self, self.get_var)

    def get_var(self):
        name = self.get_input(self.name)
        cust_path = self.get_custom_path(self.path)
        path = (
            bpy.path.abspath('//Data/')
            if self.path == ''
            else bpy.path.abspath(cust_path)
        )
        os.makedirs(path, exist_ok=True)
        return self.read_from_json(path, name)

    def read_from_json(self, path, name):
        if not path.endswith('.json'):
            path = path + f'{self.get_input(self.file_name)}.json'
        if path:
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

    def get_custom_path(self, path):
        if not path.endswith('/') and not path.endswith('json'):
            path = path + '/'
        return path


from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_WAITING
from uplogic.utils import debug
from uplogic.utils import is_waiting
import bpy
import json
import os


class ULLoadVariable(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.name = None
        self.default_value = None
        self.path = ''
        self.file_name = ''
        self.VAR = ULOutSocket(self, self.get_var)

    def get_var(self):
        socket = self.get_output('var')
        if socket is None:
            name = self.get_input(self.name)
            if is_waiting(name):
                return self.set_output('var', STATUS_WAITING)
            cust_path = self.get_custom_path(self.path)

            path = (
                bpy.path.abspath('//Data/')
                if self.path == ''
                else bpy.path.abspath(cust_path)
            )
            os.makedirs(path, exist_ok=True)

            return self.set_output(
                'var',
                self.read_from_json(path, name)
            )
        return socket

    def read_from_json(self, path, name):
        if not path.endswith('.json'):
            path = path + f'{self.file_name}.json'
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

    def evaluate(self):
        self._set_ready()

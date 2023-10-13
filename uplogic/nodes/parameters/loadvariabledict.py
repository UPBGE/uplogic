from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import debug
import bpy
import json
import os


class ULLoadVariableDict(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.file_name = None
        self.path = ''
        self.VAR = ULOutSocket(self, self.get_var)

    def get_var(self):
        cust_path = self.get_custom_path(self.path)

        path = (
            bpy.path.abspath('//Data/')
            if self.path == ''
            else bpy.path.abspath(cust_path)
        )
        os.makedirs(path, exist_ok=True)

        return self.read_from_json(path)

    def read_from_json(self, path):
        self.done = False
        if not path.endswith('.json'):
            path = path + f'{self.get_input(self.file_name)}.json'
        if not os.path.isfile(path):
            debug('No Saved Variables!')
            return
        f = open(path, 'r')
        data = json.load(f)
        f.close()
        return data

    def get_custom_path(self, path):
        if not path.endswith('/') and not path.endswith('json'):
            path = path + '/'
        return path

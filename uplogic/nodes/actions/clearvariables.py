from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import not_met
import bpy
import json
import os


class ULClearVariables(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.file_name = ''
        self.path = ''
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def write_to_json(self, path):
        data = None
        if not path.endswith('.json'):
            path = os.path.join(path, f'{self.get_input(self.file_name)}.json')
        if os.path.isfile(path):
            data = {}
            f = open(path, 'w')
            json.dump(data, f, indent=2)
        else:
            print('File does not exist - creating...')
            f = open(path, 'w')
            data = {}
            json.dump(data, f, indent=2)
        f.close()

    def evaluate(self):
        condition = self.get_input(self.condition)
        if not condition:
            return
        path = self.get_input(self.path)

        path = (bpy.path.abspath(path=path))
        os.makedirs(path, exist_ok=True)

        self.write_to_json(path)
        self._done = True

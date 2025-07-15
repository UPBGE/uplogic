from uplogic.nodes import ULActionNode
from uplogic import console
import bpy
import json
import os


class ULSaveVariableDict(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.val = None
        self.file_name = None
        self.path = ''
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def write_to_json(self, path, val):
        if not path.endswith('.json'):
            path = os.path.join(path, f'{self.get_input(self.file_name)}.json')
        if os.path.isfile(path):
            f = open(path, 'w')
            json.dump(val, f, indent=2)
        else:
            console.debug('file does not exist - creating...')
            f = open(path, 'w')
            json.dump(val, f, indent=2)
        f.close()

    def evaluate(self):
        if not self.get_condition():
            return
        val = self.get_input(self.val)

        path = self.get_input(self.path)
        path = (bpy.path.abspath(path))
        os.makedirs(path, exist_ok=True)

        self.write_to_json(path, val)
        self._done = True

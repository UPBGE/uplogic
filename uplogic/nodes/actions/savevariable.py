from uplogic.nodes import ULActionNode
from uplogic.utils import debug
import bpy
import json
import os


class ULSaveVariable(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.name = None
        self.val = None
        self.file_name = None
        self.path = ''
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def write_to_json(self, path, name, val):
        data = None
        if not path.endswith('.json'):
            path = os.path.join(path, f'{self.get_input(self.file_name)}.json')
        if os.path.isfile(path):
            f = open(path, 'r')
            data = json.load(f)
            data[name] = val
            f.close()
            f = open(path, 'w')
            json.dump(data, f, indent=2)
        else:
            debug('Variable file does not exist - creating...')
            f = open(path, 'w')
            data = {name: val}
            json.dump(data, f, indent=2)
        f.close()

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        name = self.get_input(self.name)
        val = self.get_input(self.val)

        path = self.get_input(self.path)
        path = (bpy.path.abspath(path))

        os.makedirs(path, exist_ok=True)

        self.write_to_json(path, name, val)
        self.done = True

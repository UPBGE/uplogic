from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
import bpy
import json
import os


class ULListVariables(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.print_list = None
        self.file_name = None
        self.path = ''
        self.done = None
        self.items = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.LIST = ULOutSocket(self, self.get_list)

    def get_done(self):
        return self.done

    def get_list(self):
        return self.items

    def write_to_json(self, path, p_l):
        data = None
        if not path.endswith('.json'):
            path = path + f'{self.get_input(self.file_name)}.json'
        if os.path.isfile(path):
            f = open(path, 'r')
            data = json.load(f)
            if len(data) == 0:
                print('There are no saved variables')
                return
            li = []
            for x in data:
                if p_l:
                    print('{}\t->\t{}'.format(x, data[x]))
                li.append(x)
            self.items = li
        else:
            print('There are no saved variables')
        f.close()

    def get_custom_path(self, path):
        if not path.endswith('/') and not path.endswith('json'):
            path = path + '/'
        return path

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        print_list = self.get_input(self.print_list)
        cust_path = self.get_custom_path(self.path)

        path = (
            bpy.path.abspath('//Data/')
            if self.path == ''
            else bpy.path.abspath(cust_path)
        )
        os.makedirs(path, exist_ok=True)

        self.write_to_json(path, print_list)
        self.done = True

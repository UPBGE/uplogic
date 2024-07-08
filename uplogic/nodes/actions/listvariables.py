from uplogic.nodes import ULActionNode
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
        self.OUT = self.add_output(self.get_done)
        self.LIST = self.add_output(self.get_list)

    def get_done(self):
        return self.done

    def get_list(self):
        return self.items

    def write_to_json(self, path, p_l):
        data = None
        if not path.endswith('.json'):
            path = os.path.join(path, f'{self.get_input(self.file_name)}.json')
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

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        print_list = self.get_input(self.print_list)
        path = self.get_input(self.path)

        path = (bpy.path.abspath(path))
        os.makedirs(path, exist_ok=True)

        self.write_to_json(path, print_list)
        self.done = True

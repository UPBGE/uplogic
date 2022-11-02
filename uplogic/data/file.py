import json
import os
import bpy


endings = {
    json: '.json'
}


class FileWrapper(dict):

    def __init__(self, filepath, notation=json):
        ending = endings.get(notation, '.json')
        if not filepath.endswith(ending):
            filepath = filepath + ending
        self.filepath = bpy.path.abspath(filepath)
        self.notation = notation
        self.read()

    def read(self):
        f = open(self.filepath, 'r')
        data = self.notation.load(f)
        for dat in data.keys():
            self[dat] = data[dat]
        f.close()

    def write(self):
        path = self.filepath
        notation = self.notation
        if os.path.isfile(path):
            f = open(path, 'w')
            notation.dump(self, f, indent=2)


def load_file(filepath, notation=json):
    if filepath:
        return FileWrapper(filepath, notation)
    else:
        raise FileNotFoundError(f'File {filepath} could not be opened!')


def write_file(path, name, val, notation=json):
    data = None
    ending = endings.get(notation, '.json')
    if not path.endswith(ending):
        path = path + ending
    if os.path.isfile(path):
        f = open(path, 'r')
        data = notation.load(f)
        data[name] = val
        f.close()
        f = open(path, 'w')
        notation.dump(data, f, indent=2)
    else:
        f = open(path, 'w')
        data = {name: val}
        notation.dump(data, f, indent=2)
    f.close()


def read_file(path, name, notation=json):
    data = None
    ending = endings.get(notation, '.json')
    if not path.endswith(ending):
        path = path + ending
    if os.path.isfile(path):
        f = open(path, 'r')
        data = notation.load(f)
        f.close()
        return data.get(name)

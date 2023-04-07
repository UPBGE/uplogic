import json
import toml
import configparser
import os
import bpy


class FileWrapper(dict):
    """Wrapper to allow easy access to files. The wrapper can be saved as a variable to modify and save back the file.\n
    Supports `.ini`, `.json` and `.toml` file formats.

    :param `filepath`: Full path to the file.
    """

    def __init__(self, filepath):
        self.formats = {
            'json': {'read': self._read_json, 'write': self._write_json},
            'ini': {'read': self._read_ini, 'write': self._write_ini},
            'toml': {'read': self._read_toml, 'write': self._write_toml}
        }
        self.filepath = bpy.path.abspath(filepath)
        self.read()

    @property
    def data(self):
        return dict(self)

    @data.setter
    def data(self, data: dict):
        self.clear()
        for key, value in data.items():
            self[key] = value

    def read(self):
        ending = self.filepath.split('.')[-1]
        self.formats[ending]['read']()

    def write(self):
        ending = self.filepath.split('.')[-1]
        self.formats[ending]['write']()

    def _read_json(self):
        with open(self.filepath, 'r') as f:
            self.data = json.load(f)

    def _read_toml(self):
        with open(self.filepath, 'r') as f:
            self.data = toml.load(f)

    def _read_ini(self):
        config = configparser.ConfigParser()
        config.read(self.filepath)
        for section in config.sections():
            self[section] = {}
            for key, val in config[section].items():
                self[section][key] = val

    def _write_json(self):
        path = self.filepath
        if os.path.isfile(path):
            with open(path, 'w') as f:
                json.dump(self, f, indent=2)

    def _write_toml(self):
        path = self.filepath
        if os.path.isfile(path):
            with open(path, 'w') as f:
                toml.dump(self.data, f)

    def _write_ini(self):
        config = configparser.ConfigParser()
        config.read_dict(self)
        with open(self.filepath, 'w') as f:
            config.write(f)


def load_file(filepath) -> FileWrapper:
    """Read a file and keep it stored for later use.\n
    Supports `.ini`, `.json` and `.toml` file formats.

    :param `filepath`: Full path to the file.
    """
    if filepath:
        return FileWrapper(filepath)
    else:
        raise FileNotFoundError(f'File {filepath} could not be opened!')


def write_file(filepath, data) -> None:
    """Write data in form of `dict` back into a file.\n
    Supports `.ini`, `.json` and `.toml` file formats.

    :param `filepath`: Full path to the file.
    :param `data`: `dict` to save back into the file.
    """
    file = FileWrapper(filepath)
    file.data = data
    file.write()


def read_file(filepath) -> dict:
    """Read data in form of `dict` from a file.\n
    Supports `.ini`, `.json` and `.toml` file formats.

    :param `filepath`: Full path to the file.
    """
    return FileWrapper(filepath).data

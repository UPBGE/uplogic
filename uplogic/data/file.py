'''File I/O helpers for uplogic.

Provides :class:`FileWrapper`, a ``dict`` subclass that reads and writes
``.json`` and ``.ini`` files, and three convenience functions
(:func:`load_file`, :func:`read_file`, :func:`write_file`) for one-shot
access.
'''

import json
# import toml
import configparser
import os
import bpy


class FileWrapper(dict):
    '''``dict`` subclass that reads and writes a file on disk.

    The file is read on construction and the contents are accessible as
    dictionary keys.  Call :meth:`write` (or the alias :meth:`save`) to
    persist any changes back to disk.

    Supports ``.json`` and ``.ini`` file formats; the format is detected from
    the file extension.

    :param filepath: Blender-relative or absolute path to the file.
    '''

    def __init__(self, filepath):
        self.formats = {
            'json': {'read': self._read_json, 'write': self._write_json},
            'ini': {'read': self._read_ini, 'write': self._write_ini}
            # 'toml': {'read': self._read_toml, 'write': self._write_toml}
        }
        self.filepath = bpy.path.abspath(filepath)
        self.read()

    @property
    def data(self):
        '''The file contents as a plain ``dict``. Setting this replaces all
        current entries and also creates matching instance attributes for
        each key.
        '''
        return dict(self)

    @data.setter
    def data(self, data: dict):
        self.clear()
        for key, value in data.items():
            self[key] = value
            setattr(self, key, value)

    def read(self):
        '''Re-read the file from disk, replacing the current contents.

        The format is inferred from the file extension.
        '''
        ending = self.filepath.split('.')[-1]
        self.formats[ending]['read']()

    def write(self):
        '''Write the current contents back to disk.

        The format is inferred from the file extension.
        '''
        ending = self.filepath.split('.')[-1]
        self.formats[ending]['write']()

    def save(self):
        '''Alias for :meth:`write`.'''
        self.write()

    def _read_json(self):
        '''Load a JSON file into the wrapper dict.'''
        with open(self.filepath, 'r') as f:
            self.data = json.load(f)

    # def _read_toml(self):
    #     with open(self.filepath, 'r') as f:
    #         self.data = toml.load(f)

    def _read_ini(self):
        '''Load an INI file; each section becomes a nested ``dict`` entry.'''
        config = configparser.ConfigParser()
        config.read(self.filepath)
        for section in config.sections():
            self[section] = {}
            for key, val in config[section].items():
                self[section][key] = val

    def _write_json(self):
        '''Write the current dict contents to the JSON file with 2-space indentation.'''
        path = self.filepath
        if os.path.isfile(path):
            with open(path, 'w') as f:
                json.dump(self, f, indent=2)

    # def _write_toml(self):
    #     path = self.filepath
    #     if os.path.isfile(path):
    #         with open(path, 'w') as f:
    #             toml.dump(self.data, f)

    def _write_ini(self):
        '''Write the current dict contents back to the INI file.'''
        config = configparser.ConfigParser()
        config.read_dict(self)
        with open(self.filepath, 'w') as f:
            config.write(f)


def load_file(filepath) -> FileWrapper:
    '''Open a file and return a live :class:`FileWrapper` for it.

    The wrapper holds the file contents as a ``dict`` and can be written back
    to disk with :meth:`~FileWrapper.write`.  Supports ``.json`` and ``.ini``.

    :param filepath: Blender-relative or absolute path to the file.
    :returns: A :class:`FileWrapper` populated with the file's contents.
    :raises FileNotFoundError: When *filepath* is falsy.
    '''
    if filepath:
        return FileWrapper(filepath)
    else:
        raise FileNotFoundError(f'File {filepath} could not be opened!')


def write_file(filepath, data) -> None:
    '''Write *data* to a file, overwriting its current contents.

    Supports ``.json`` and ``.ini`` file formats; the format is detected from
    the file extension.

    :param filepath: Blender-relative or absolute path to the file.
    :param data: ``dict`` to write into the file.
    '''
    file = FileWrapper(filepath)
    file.data = data
    file.write()


def read_file(filepath) -> dict:
    '''Read a file and return its contents as a plain ``dict``.

    Supports ``.json`` and ``.ini`` file formats; the format is detected from
    the file extension.

    :param filepath: Blender-relative or absolute path to the file.
    :returns: ``dict`` of the file's contents.
    '''
    return FileWrapper(filepath).data

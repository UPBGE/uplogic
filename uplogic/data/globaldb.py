'''Persistent key-value store for uplogic.

:class:`GlobalDB` is a lightweight, named database that lives for the
lifetime of the Python interpreter.  Values can optionally be written to
a plain-text file on disk so they survive game restarts.

Typical usage::

    from uplogic.data import GlobalDB

    db = GlobalDB.retrieve('my_save')
    db.put('score', 42, persist=True)   # written to disk immediately
    score = db.get('score', 0)
'''

from bge import logic
import bpy
import os
from uplogic.utils import unload_nodes
from uplogic import console


class GlobalDB(object):
    '''Named key-value store with optional disk persistence.

    Values survive for the lifetime of the Python interpreter and are shared
    across all code that calls :meth:`retrieve` with the same name.  When
    *persist* is ``True`` on :meth:`put`, the value is also appended to a
    plain-text ``*.logdb.txt`` file so it can be restored across game restarts.

    Instances are never created directly; use :meth:`retrieve` to get or
    create a named database.
    '''

    index: int
    initialized: bool = False

    class LineBuffer(object):
        '''Simple line-oriented read/write buffer backed by a list of strings.

        Used internally to serialise and deserialise :class:`GlobalDB` entries.
        '''

        def __init__(self, buffer=[]):
            self.buffer = buffer
            self.index = 0
            self.size = len(self.buffer)

        def read(self):
            '''Return the next line and advance the read cursor.'''
            line = self.buffer[self.index]
            self.index += 1
            return line

        def write(self, line):
            '''Append *line* followed by a newline to the buffer.'''
            self.buffer.append(line + "\n")

        def has_next(self):
            '''``True`` while there are unread lines remaining.'''
            return self.index < self.size

        def flush(self, file):
            '''Append all buffered lines to *file* on disk.

            :param file: Filesystem path to the target file.
            '''
            with open(file, "a") as f:
                f.writelines(self.buffer)

    class Serializer(object):
        '''Abstract base for type-specific value serialisers used by :class:`GlobalDB`.

        Subclasses must implement :meth:`read` and :meth:`write`.
        '''

        def read(self, line_reader):
            '''Deserialise a value from *line_reader*.

            :param line_reader: A :class:`~GlobalDB.LineBuffer` positioned at
                the first line of this value's encoding.
            :returns: The deserialised value.
            '''
            raise NotImplementedError()

        def write(self, value, line_writer):
            '''Serialise *value* into *line_writer*.

            :param value: The value to encode.
            :param line_writer: A :class:`~GlobalDB.LineBuffer` to write lines into.
            '''
            raise NotImplementedError()

    serializers = {}
    storage_dir = logic.expandPath("//Globals")
    shared_dbs = {}

    @classmethod
    def retrieve(cls, fname):
        '''Return the named :class:`GlobalDB`, creating it if it does not exist.

        :param fname: Unique name that identifies this database.
        :returns: The :class:`GlobalDB` instance for *fname*.
        '''
        db = cls.shared_dbs.get(fname)
        if db is None:
            db = GlobalDB(fname)
            cls.shared_dbs[fname] = db
        return db

    @classmethod
    def get_storage_dir(cls):
        '''Return the filesystem path where ``*.logdb.txt`` files are written.

        :returns: Absolute path to the storage directory.
        '''
        return cls.storage_dir

    @classmethod
    def put_value(cls, key, value, buffer):
        '''Serialise a single *key*/*value* pair into *buffer* using the
        registered serialiser for the value's type.

        Writes three header lines (``"PUT"``, key, type name) followed by
        the type-specific payload.  Does nothing and returns ``False`` if no
        serialiser is registered for the type.

        :param key: String key to record.
        :param value: Value to serialise.
        :param buffer: A :class:`~GlobalDB.LineBuffer` to write into.
        '''
        type_name = str(type(value))
        serializer = cls.serializers.get(type_name)
        if not serializer:
            return False
        buffer.write("PUT")
        buffer.write(key)
        buffer.write(type_name)
        serializer.write(value, buffer)

    @classmethod
    def read_existing(cls, fpath, intodic):
        '''Read all entries from an existing ``*.logdb.txt`` file into *intodic*.

        :param fpath: Absolute path to the log file.
        :param intodic: ``dict`` that receives the deserialised key/value pairs.
        :returns: Number of entries read.
        '''
        lines = []
        with open(fpath, "r") as f:
            lines.extend(f.read().splitlines())
        buffer = GlobalDB.LineBuffer(lines)
        log_size = 0
        while buffer.has_next():
            op = buffer.read()
            assert op == "PUT"
            key = buffer.read()
            type_id = buffer.read()
            serializer = GlobalDB.serializers.get(type_id)
            value = serializer.read(buffer)
            intodic[key] = value
            log_size += 1
        return log_size

    @classmethod
    def write_put(cls, fname, key, value):
        '''Append a single persistent key/value entry to the on-disk log for
        the database named *fname*.

        Creates the storage directory if it does not yet exist.  Silently
        returns if no serialiser is registered for *value*'s type.

        :param fname: Name of the target database.
        :param key: Key to persist.
        :param value: Value to persist.
        '''
        type_name = str(type(value))
        serializer = cls.serializers.get(type_name)
        if not serializer:
            return  # no serializer for given value type
        if not os.path.exists(cls.get_storage_dir()):
            os.mkdir(cls.get_storage_dir())
        fpath = os.path.join(
            cls.get_storage_dir(),
            "{}.logdb.txt".format(fname)
        )
        buffer = GlobalDB.LineBuffer()
        cls.put_value(key, value, buffer)
        buffer.flush(fpath)

    @classmethod
    def read(cls, fname, intodic):
        '''Load all persisted entries for *fname* into *intodic* if a log file
        exists, otherwise return ``0``.

        :param fname: Name of the database to load.
        :param intodic: ``dict`` that receives the loaded entries.
        :returns: Number of entries loaded, or ``0`` if no file was found.
        '''
        fpath = os.path.join(
            cls.get_storage_dir(),
            "{}.logdb.txt".format(fname)
        )
        if os.path.exists(fpath):
            return cls.read_existing(fpath, intodic)
        else:
            return 0

    @classmethod
    def compress(cls, fname, content):
        '''Rewrite the on-disk log for *fname* from scratch using only the
        current *content*, discarding stale entries accumulated by previous
        appends.

        :param fname: Name of the database whose log file should be rewritten.
        :param content: ``dict`` of the current key/value pairs to persist.
        '''
        buffer = GlobalDB.LineBuffer()
        for key in content:
            value = content[key]
            cls.put_value(key, value, buffer)
        fpath = os.path.join(
            cls.get_storage_dir(),
            "{}.logdb.txt".format(fname)
        )
        with open(fpath, "w") as f:
            f.writelines(buffer.buffer)

    def __init__(self, file_name):
        self.fname = file_name
        self.locked = {}
        self.content = {}

        filter(
            lambda a: a.__name__ == 'unload_nodes',
            bpy.app.handlers.game_post
        )
        remove_f = []
        for f in bpy.app.handlers.game_post:
            if f.__name__ == 'unload_nodes':
                remove_f.append(f)
        for f in remove_f:
            bpy.app.handlers.game_post.remove(f)
        bpy.app.handlers.game_post.append(unload_nodes)

        log_size = GlobalDB.read(self.fname, self.content)
        if log_size > (5 * len(self.content)):
            console.debug("Compressing sld {}".format(file_name))
            GlobalDB.compress(self.fname, self.content)

    def lock(self, item, event):
        '''Associate *event* with *item* so it can be released later via
        :meth:`unlock`.

        :param item: Key to lock.
        :param event: Arbitrary value to store alongside the lock.
        '''
        self.locked[item] = event

    def unlock(self, item):
        '''Release the lock previously set for *item* via :meth:`lock`.

        :param item: Key to unlock.
        '''
        self.locked.pop(item)

    def get(self, key, default_value=None):
        '''Return the value stored under *key*, or *default_value* if absent.

        :param key: Key to look up.
        :param default_value: Fallback returned when *key* is not present.
        :returns: The stored value or *default_value*.
        '''
        if not key:
            return default_value
        return self.content.get(key, default_value)

    def clear(self):
        '''Remove all entries from the in-memory store.

        Does not delete any on-disk log file.
        '''
        self.content.clear()

    def put(self, key, value, persist=False):
        '''Store *value* under *key*.

        When *persist* is ``True`` and the value has changed, the new entry is
        also appended to the on-disk log via :meth:`~GlobalDB.write_put`.

        :param key: Key to store the value under.
        :param value: Value to store.
        :param persist: When ``True``, write to disk if the value changed.
        '''
        self.content[key] = value
        if persist:
            old_value = self.content.get(key)
            changed = old_value != value
            if changed:
                GlobalDB.write_put(self.fname, key, value)

    def check(self, key):
        '''Return ``True`` if *key* is present in the store.

        :param key: Key to check.
        :returns: ``True`` if the key exists, ``False`` otherwise.
        '''
        valid = key in self.content
        return valid

    def pop(self, key, default=None):
        '''Remove and return the value stored under *key*.

        :param key: Key to remove.
        :param default: Returned when *key* is absent.
        :returns: The removed value or *default*.
        '''
        if not key:
            return default
        return self.content.pop(key, default)

    def remove(self, key):
        '''Delete *key* from the store if it exists (no-op otherwise).

        :param key: Key to delete.
        '''
        if key in self.content.keys():
            del self.content[key]

    def log(self):
        '''Print the entire contents of this database to the uplogic console.'''
        console.log(self.content)


def store(key, value, category='uplogic.default_globals', persist=False):
    '''Store *value* under *key* in the named global category.

    Calls :func:`initialize` to load scene-defined globals before writing.

    :param key: Key to store the value under.
    :param value: Value to store.
    :param category: Name of the :class:`GlobalDB` to write to.
    :param persist: When ``True``, write the entry to disk.
    '''
    initialize()
    values = GlobalDB.retrieve(category)
    values.put(key, value, persist)


def retrieve(key, category='uplogic.default_globals', default=None):
    '''Retrieve a value from the named global category.

    Calls :func:`initialize` to load scene-defined globals before reading.

    :param key: Key to look up.
    :param category: Name of the :class:`GlobalDB` to read from.
    :param default: Returned when *key* is absent.
    :returns: The stored value or *default*.
    '''
    initialize()
    values = GlobalDB.retrieve(category)
    return values.get(key, default)


def get_category(name='uplogic.default_globals'):
    '''Return the :class:`GlobalDB` for *name*, creating it if needed.

    :param name: Database name.
    :returns: The :class:`GlobalDB` instance.
    '''
    return GlobalDB.retrieve(name)


def initialize():
    '''Load global categories defined on the current Blender scene into their
    respective :class:`GlobalDB` instances.

    Only runs once per Python session (:attr:`GlobalDB.initialized` is set to
    ``True`` afterwards).  Called automatically by :func:`store` and
    :func:`retrieve`.
    '''
    if not GlobalDB.initialized:
        scene = logic.getCurrentScene()
        cats = getattr(
            bpy.data.scenes[scene.name],
            'nl_global_categories',
            None
        )
        if not cats:
            return

        msg = ''

        dat = {
            'STRING': 'string_val',
            'FLOAT': 'float_val',
            'INTEGER': 'int_val',
            'BOOLEAN': 'bool_val',
            'FILE_PATH': 'filepath_val'
        }

        for c in cats:
            db = GlobalDB.retrieve(c.name)
            msg += f' {c.name},'
            for v in c.content:
                val = getattr(v, dat.get(v.value_type, 'FLOAT'), 0)
                db.put(v.name, val, v.persistent)

        if msg:
            console.success(f'Globals Initialized:{msg[:-1]}')
        GlobalDB.initialized = True
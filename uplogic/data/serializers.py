'''Concrete :class:`~uplogic.data.GlobalDB.Serializer` implementations for
the types registered by default in :mod:`uplogic.data`.

Each serialiser handles one Python type and knows how to encode/decode it
using a :class:`~uplogic.data.GlobalDB.LineBuffer`.
'''

from uplogic.data import GlobalDB
from mathutils import Vector


class StringSerializer(GlobalDB.Serializer):
    '''Serialiser for ``str`` values.

    Writes the string as a single line; reads it back, converting the literal
    ``"None"`` to ``None``.
    '''

    def write(self, value, line_writer):
        '''Write *value* as a single line.

        :param value: ``str`` to encode.
        :param line_writer: Target :class:`~uplogic.data.GlobalDB.LineBuffer`.
        '''
        line_writer.write(value)

    def read(self, line_reader):
        '''Read one line and return it as a ``str``, or ``None`` for ``"None"``.

        :param line_reader: Source :class:`~uplogic.data.GlobalDB.LineBuffer`.
        :returns: ``str`` or ``None``.
        '''
        data = line_reader.read()
        return None if data == "None" else data


class FloatSerializer(GlobalDB.Serializer):
    '''Serialiser for ``float`` values.'''

    def write(self, value, line_writer):
        '''Write *value* as its string representation.

        :param value: ``float`` to encode.
        :param line_writer: Target :class:`~uplogic.data.GlobalDB.LineBuffer`.
        '''
        line_writer.write(str(value))

    def read(self, line_reader):
        '''Read one line and return it as a ``float``, or ``None`` for ``"None"``.

        :param line_reader: Source :class:`~uplogic.data.GlobalDB.LineBuffer`.
        :returns: ``float`` or ``None``.
        '''
        data = line_reader.read()
        return None if data == "None" else float(data)


class IntegerSerializer(GlobalDB.Serializer):
    '''Serialiser for ``int`` values.'''

    def write(self, value, line_writer):
        '''Write *value* as its string representation.

        :param value: ``int`` to encode.
        :param line_writer: Target :class:`~uplogic.data.GlobalDB.LineBuffer`.
        '''
        line_writer.write(str(value))

    def read(self, line_reader):
        '''Read one line and return it as an ``int``, or ``None`` for ``"None"``.

        :param line_reader: Source :class:`~uplogic.data.GlobalDB.LineBuffer`.
        :returns: ``int`` or ``None``.
        '''
        data = line_reader.read()
        return None if data == "None" else int(data)


class ListSerializer(GlobalDB.Serializer):
    '''Serialiser for ``list`` and ``tuple`` values.

    Encodes each element using the serialiser registered for its own type,
    prefixed by the element count so the reader knows how many entries to
    reconstruct.
    '''

    def write(self, value, line_writer):
        '''Write *value* as a count line followed by type-tagged element lines.

        Elements whose type has no registered serialiser are silently skipped.

        :param value: ``list`` or ``tuple`` to encode.
        :param line_writer: Target :class:`~uplogic.data.GlobalDB.LineBuffer`.
        '''
        line_writer.write(str(len(value)))
        for e in value:
            tp = str(type(e))
            serializer = GlobalDB.serializers.get(tp)
            if serializer:
                line_writer.write(tp)
                serializer.write(e, line_writer)

    def read(self, line_reader):
        '''Read a count line then that many type-tagged elements.

        :param line_reader: Source :class:`~uplogic.data.GlobalDB.LineBuffer`.
        :returns: ``list`` of the deserialised elements.
        '''
        data = []
        count = int(line_reader.read())
        for i in range(0, count):
            tp = line_reader.read()
            serializer = GlobalDB.serializers.get(tp)
            value = serializer.read(line_reader)
            data.append(value)
        return data


class VectorSerializer(GlobalDB.Serializer):
    '''Serialiser for :class:`mathutils.Vector` values.

    Encodes components as space-separated floats on a single line.
    '''

    def write(self, value, line_writer):
        '''Write *value*'s components as a space-separated string, or ``"None"``
        when *value* is ``None``.

        :param value: :class:`mathutils.Vector` or ``None`` to encode.
        :param line_writer: Target :class:`~uplogic.data.GlobalDB.LineBuffer`.
        '''
        if value is None:
            line_writer.write("None")
        else:
            line = ""
            for i in value:
                line += str(i) + " "
            line_writer.write(line)

    def read(self, line_reader):
        '''Read a space-separated component line and return a
        :class:`mathutils.Vector`, or ``None`` for ``"None"``.

        :param line_reader: Source :class:`~uplogic.data.GlobalDB.LineBuffer`.
        :returns: :class:`mathutils.Vector` or ``None``.
        '''
        line = line_reader.read()
        if line == "None":
            return None
        data = line.rstrip().split(" ")
        components = [float(d) for d in data]
        return Vector(components)

from .globaldb import GlobalDB
from .globaldb import retrieve  # noqa
from .globaldb import store  # noqa
from .file import read_file  # noqa
from .file import write_file  # noqa
from .file import load_file  # noqa
from .serializers import StringSerializer
from .serializers import FloatSerializer
from .serializers import IntegerSerializer
from .serializers import ListSerializer
from .serializers import VectorSerializer
from mathutils import Vector
from bge.types import KX_PythonComponent
from bge.types import KX_GameObject


GlobalDB.serializers[str(type(""))] = StringSerializer()
GlobalDB.serializers[str(type(1.0))] = FloatSerializer()
GlobalDB.serializers[str(type(10))] = IntegerSerializer()
GlobalDB.serializers[str(type([]))] = ListSerializer()
GlobalDB.serializers[str(type((0, 0, 0)))] = ListSerializer()
GlobalDB.serializers[str(type(Vector()))] = (
    VectorSerializer()
)


class GameProperty():

    def __init__(self, inst, name, default=None):
        
        def getPropComponent(self, attr_name=name):
                return self.object.get(attr_name)

        def setPropComponent(self, value, attr_name=name):
            self.object[attr_name] = value

        def getPropObject(self, attr_name=name):
            return self.get(attr_name)

        def setPropObject(self, value, attr_name=name):
            self[attr_name] = value

        if issubclass(inst.__class__, KX_PythonComponent):
            prop = property(getPropComponent, setPropComponent)
            if default:
                inst.object[name] = default
        elif issubclass(inst.__class__, KX_GameObject):
            prop = property(getPropObject, setPropObject)
            if default:
                inst[name] = default
        else:
            return
        setattr(inst.__class__, name, prop)


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


import bpy
from bge import logic


def init_glob_cats():
    # if not hasattr(bpy.types.Scene, 'nl_globals_initialized'):
    scene = logic.getCurrentScene()
    cats = getattr(
        bpy.data.scenes[scene.name],
        'nl_global_categories',
        None
    )
    print(cats)
    if not cats:
        print('No global categories found in', bpy.data.scenes[scene.name], bpy.data.scenes)
        return
    print(bpy.data.scenes[scene.name], bpy.data.scenes)

    msg = ''

    dat = {
        '0': 'float_val',
        '1': 'string_val',
        '2': 'int_val',
        '3': 'bool_val',
        '17': 'filepath_val',
        '4': 'vec_val',
        '5': 'color_val',
        '6': 'color_alpha_val',
        '7': 'obj_val',
        '8': 'collection_val',
        '9': 'material_val',
        '10': 'mesh_val',
        '11': 'node_tree_val',
        '12': 'action_val',
        '13': 'text_val',
        '14': 'sound_val',
        '15': 'image_val',
        '16': 'font_val'
    }

    for c in cats:
        db = GlobalDB.retrieve(c.name)
        msg += f' {c.name},'
        for v in c.content:
            val = getattr(v, dat.get(v.value_type, '0'), 0)
            if isinstance(val, bpy.types.Object):
                val = logic.getCurrentScene().getGameObjectFromObject(val)
            elif int(v.value_type) in [4, 5, 6]:
                val = Vector(val)
            db.put(v.name, val, v.persistent)

    if msg:
        print(f'Globals Initialized:{msg[:-1]}')
    bpy.types.Scene.nl_globals_initialized = True


print(bpy.data.filepath)
# print(bpy.context.scene.nl_global_categories)
print(bpy.context.scene.objects['Cube'].logic_trees)
print('AAAAAAAAAAAAAAAAAAAA', hasattr(bpy.types.Scene, 'nl_globals_initialized'))
init_glob_cats()

# if init_glob_cats not in bpy.app.handlers.load_post:
#     bpy.app.handlers.load_post.append(init_glob_cats)
import bge, bpy


class classproperty(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)

class Engine(object):

    _pre_draw = None
    _post_draw = None
    _pre_draw_setup = None

    @classproperty
    def bge_scene(cls) -> bge.types.KX_Scene:
        bge.logic.getCurrentScene()
    
    @classproperty
    def bpy_scene(cls):
        return bpy.data.scenes[cls.bge_scene.name]

    @classproperty
    def pre_draw(cls):
        scene = cls.bpy_scene
        return (
            cls.bpy_scene.pre_draw
            if scene.game_settings.use_viewport_renderer else
            cls.bge_scene.pre_draw
        )

    @pre_draw.setter
    def pre_draw(cls, value):
        return

    @classproperty
    def post_draw(cls):
        return cls._bar

    @post_draw.setter
    def post_draw(cls, value):
        return

    @classproperty
    def pre_draw_setup(cls):
        return cls._bar

    @pre_draw_setup.setter
    def pre_draw_setup(cls, value):
        return
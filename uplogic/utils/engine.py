'''Engine-level descriptor utilities for uplogic.
'''
import bge, bpy


class classproperty(object):
    '''Descriptor that exposes a method as a class-level property.

    Decorating a method with ``@classproperty`` causes attribute access on
    either an instance or the class itself to invoke the method with the
    *owner* class as the sole argument, mimicking the behaviour of a
    ``@property`` but at the class level.
    '''

    def __init__(self, f):
        '''Store the decorated callable *f* for later invocation.

        :param f: The callable to wrap. It must accept a single positional
            argument — the owner class.
        '''
        self.f = f

    def __get__(self, obj, owner):
        '''Invoke the wrapped callable with *owner* and return the result.

        Called automatically by Python's attribute-lookup machinery whether
        access originates from an instance or from the class directly.

        :param obj: The instance through which the attribute was accessed, or
            ``None`` when accessed directly on the class.
        :param owner: The class that owns the descriptor.
        :returns: The return value of ``self.f(owner)``.
        '''
        return self.f(owner)

# class Engine(object):

#     _pre_draw = None
#     _post_draw = None
#     _pre_draw_setup = None

#     @classproperty
#     def bge_scene(cls) -> bge.types.KX_Scene:
#         bge.logic.getCurrentScene()

#     @classproperty
#     def bpy_scene(cls):
#         return bpy.data.scenes[cls.bge_scene.name]

#     @classproperty
#     def pre_draw(cls):
#         scene = cls.bpy_scene
#         return (
#             cls.bpy_scene.pre_draw
#             if scene.game_settings.use_viewport_renderer else
#             cls.bge_scene.pre_draw
#         )

#     @pre_draw.setter
#     def pre_draw(cls, value):
#         return

#     @classproperty
#     def post_draw(cls):
#         return cls._bar

#     @post_draw.setter
#     def post_draw(cls, value):
#         return

#     @classproperty
#     def pre_draw_setup(cls):
#         return cls._bar

#     @pre_draw_setup.setter
#     def pre_draw_setup(cls, value):
#         return


# def pre_draw(cb):
#     print(cb.__self__)
#     scene = bge.logic.getCurrentScene()
#     scene.pre_draw.append(cb)
    # scene = Engine.bpy_scene
    # return (
    #     Engine.bpy_scene.pre_draw
    #     if scene.game_settings.use_viewport_renderer else
    #     Engine.bge_scene.pre_draw

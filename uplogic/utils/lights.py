'''BGE light utilities for uplogic — creating, wrapping, and modifying scene lights.
'''
from bge.types import KX_GameObject
from bge import logic
from bpy.types import Object
import bpy
from mathutils import Vector, Matrix, Color
from .objects import GameObject
from uplogic import console


def make_unique_light(light: KX_GameObject) -> KX_GameObject:
    '''Copy this light's Blender data block so it can be modified without affecting other
    objects that share the same ``KX_LightObject`` data.

    :param light: The ``KX_LightObject`` whose data block will be duplicated.
    :returns: The same ``KX_LightObject`` passed as *light*, now owning its own
        independent data block.
    '''
    lamp = light.blenderObject
    lamp.data = lamp.data.copy()
    return light


class Light(GameObject):
    '''Wrapper for a ``KX_LightObject``.

    Can either wrap an existing scene light or create an entirely new one.  When
    *light* is supplied the object is wrapped in-place and :func:`make_unique_light`
    is called so later property changes do not bleed into other objects sharing the
    same data block.  When *light* is ``None`` a new Blender light data-block of the
    requested *type* is created, linked into the active scene collection, and
    converted to a ``KX_LightObject``.

    :param name: Name for the new light object (used only when *light* is ``None``).
    :param type: Light type for the new data-block; one of ``"POINT"``, ``"SUN"``,
        ``"SPOT"``, or ``"AREA"`` (used only when *light* is ``None``).
    :param light: Existing ``KX_GameObject`` to wrap.  Leave at ``None`` to create
        a brand-new light.
    '''

    _deprecated = False

    def __init__(
        self,
        name: str = '',
        type: str = 'POINT',
        light: KX_GameObject = None
    ) -> None:
        if self._deprecated:
            console.warning('[UPLOGIC] ULLight class will be renamed to "Light" in future releases!')
        if light:
            self.game_object = make_unique_light(light)
            '''The wrapped ``KX_LightObject``.'''
            return
        game_scene = logic.getCurrentScene()
        scene = bpy.data.scenes[game_scene.name]
        light = bpy.data.lights.new(name, type)
        light = bpy.data.objects.new(name, light)
        scene.collection.objects.link(light)
        self.game_object = game_scene.convertBlenderObject(light)
        '''The wrapped ``KX_LightObject``.'''
        self.energy = 10

    @property
    def energy(self) -> float:
        '''Lamp energy (luminous power), delegating to ``blenderObject.data.energy``.
        '''
        return self.game_object.blenderObject.data.energy

    @energy.setter
    def energy(self, val: float):
        self.game_object.blenderObject.data.energy = val

    @property
    def color(self) -> Color:
        '''Lamp colour as ``mathutils.Color``, delegating to ``blenderObject.data.color``.
        '''
        return self.game_object.blenderObject.data.color

    @color.setter
    def color(self, val: Color):
        self.game_object.blenderObject.data.color = val

    @property
    def use_shadow(self) -> bool:
        '''Whether the lamp casts shadows, delegating to ``blenderObject.data.use_shadow``.
        '''
        return self.game_object.blenderObject.data.use_shadow

    @use_shadow.setter
    def use_shadow(self, val: bool):
        self.game_object.blenderObject.data.use_shadow = val

    @property
    def shadow_clip_start(self) -> float:
        '''Shadow buffer near clipping distance, delegating to
        ``blenderObject.data.shadow_buffer_clip_start``.
        '''
        return self.game_object.blenderObject.data.shadow_buffer_clip_start

    @shadow_clip_start.setter
    def shadow_clip_start(self, val: float):
        self.game_object.blenderObject.data.shadow_buffer_clip_start = val

    @property
    def shadow_bias(self) -> float:
        '''Shadow buffer depth bias, delegating to
        ``blenderObject.data.shadow_buffer_bias``.
        '''
        return self.game_object.blenderObject.data.shadow_buffer_bias

    @shadow_bias.setter
    def shadow_bias(self, val: float):
        self.game_object.blenderObject.data.shadow_buffer_bias = val

    @property
    def use_custom_distance(self) -> bool:
        '''Whether a custom cutoff distance is active, delegating to
        ``blenderObject.data.use_custom_distance``.
        '''
        return self.game_object.blenderObject.data.use_custom_distance

    @use_custom_distance.setter
    def use_custom_distance(self, val: bool):
        self.game_object.blenderObject.data.use_custom_distance = val

    @property
    def distance(self) -> float:
        '''Lamp cutoff distance (effective only when ``use_custom_distance`` is ``True``),
        delegating to ``blenderObject.data.cutoff_distance``.
        '''
        return self.game_object.blenderObject.data.cutoff_distance

    @distance.setter
    def distance(self, val: float):
        self.game_object.blenderObject.data.cutoff_distance = val

    @property
    def angle(self) -> float:
        '''Area light opening angle in radians, delegating to
        ``blenderObject.data.angle``.
        '''
        return self.game_object.blenderObject.data.angle

    @angle.setter
    def angle(self, val: float):
        self.game_object.blenderObject.data.angle = val

    @property
    def spot_size(self) -> float:
        '''Spotlight cone angle in radians, delegating to
        ``blenderObject.data.spot_size``.
        '''
        return self.game_object.blenderObject.data.spot_size

    @spot_size.setter
    def spot_size(self, val: float):
        self.game_object.blenderObject.data.spot_size = val

    @property
    def spot_blend(self) -> float:
        '''Spotlight edge softness factor, delegating to
        ``blenderObject.data.spot_blend``.
        '''
        return self.game_object.blenderObject.data.spot_blend

    @spot_blend.setter
    def spot_blend(self, val: float):
        self.game_object.blenderObject.data.spot_blend = val

    @property
    def radius(self) -> float:
        '''Soft-shadow source radius, delegating to
        ``blenderObject.data.shadow_soft_size``.
        '''
        return self.game_object.blenderObject.data.shadow_soft_size

    @radius.setter
    def radius(self, val: float):
        self.game_object.blenderObject.data.shadow_soft_size = val


class ULLight(Light):
    '''[DEPRECATED] Use :class:`Light` instead.
    '''
    _deprecated = True

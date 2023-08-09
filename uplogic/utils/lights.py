from bge.types import KX_GameObject
from bge import logic
from bpy.types import Object
import bpy
from mathutils import Vector, Matrix, Color
from .objects import GameObject


def make_unique_light(light: KX_GameObject) -> KX_GameObject:
    '''Make a copy of this light to allow for unique modifications.

    :param `light`: The `KX_LightObject` of which to copy the data.

    :returns: The modified `KX_LightObject`. This return value is for usability reasons and
    is the same as the original argument.
    '''
    lamp = light.blenderObject
    lamp.data = lamp.data.copy()
    return light


class ULLight(GameObject):
    """Wrapper for `KX_LightObject`. Can either convert a given scene light or create a new one.

    :param `name`: The name of the new light (only relevant if `light` argument is None).
    :param `type`: The type of the new light of [`"POINT"`, `"SUN"`, `"SPOT"`, `"AREA"`] (only relevant if `light` argument is None).
    :param `light`: The scene light to be converted. Leave at `None` to create new.
    """

    _deprecated = True

    def __init__(
        self,
        name: str = '',
        type: str = 'POINT',
        light: KX_GameObject = None
    ) -> None:
        if self._deprecated:
            print('[UPLOGIC] ULLight class will be renamed to "Light" in future releases!')
        if light:
            self.game_object = make_unique_light(light)
            """The wrapped `KX_LightObject`."""
            return
        game_scene = logic.getCurrentScene()
        scene = bpy.data.scenes[game_scene.name]
        light = bpy.data.lights.new(name, type)
        light = bpy.data.objects.new(name, light)
        scene.collection.objects.link(light)
        self.game_object = game_scene.convertBlenderObject(light)
        """The wrapped `KX_LightObject`."""
        self.energy = 10

    @property
    def energy(self) -> float:
        return self.game_object.blenderObject.data.energy

    @energy.setter
    def energy(self, val: float):
        self.game_object.blenderObject.data.energy = val

    @property
    def color(self) -> Color:
        return self.game_object.blenderObject.data.color

    @color.setter
    def color(self, val: Color):
        self.game_object.blenderObject.data.color = val

    @property
    def use_shadow(self) -> bool:
        return self.game_object.blenderObject.data.use_shadow

    @use_shadow.setter
    def use_shadow(self, val: bool):
        self.game_object.blenderObject.data.use_shadow = val

    @property
    def shadow_clip_start(self) -> float:
        return self.game_object.blenderObject.data.shadow_buffer_clip_start

    @shadow_clip_start.setter
    def shadow_clip_start(self, val: float):
        self.game_object.blenderObject.data.shadow_buffer_clip_start = val

    @property
    def shadow_bias(self) -> float:
        return self.game_object.blenderObject.data.shadow_buffer_bias

    @shadow_bias.setter
    def shadow_bias(self, val: float):
        self.game_object.blenderObject.data.shadow_buffer_bias = val

    @property
    def use_custom_distance(self) -> bool:
        return self.game_object.blenderObject.data.use_custom_distance

    @use_custom_distance.setter
    def use_custom_distance(self, val: bool):
        self.game_object.blenderObject.data.use_custom_distance = val

    @property
    def distance(self) -> float:
        return self.game_object.blenderObject.data.cutoff_distance

    @distance.setter
    def distance(self, val: float):
        self.game_object.blenderObject.data.cutoff_distance = val

    @property
    def angle(self)-> float:
        return self.game_object.blenderObject.data.angle

    @angle.setter
    def angle(self, val: float):
        self.game_object.blenderObject.data.angle = val

    @property
    def spot_size(self) -> float:
        return self.game_object.blenderObject.data.spot_size

    @spot_size.setter
    def spot_size(self, val: float):
        self.game_object.blenderObject.data.spot_size = val

    @property
    def spot_blend(self) -> float:
        return self.game_object.blenderObject.data.spot_blend

    @spot_blend.setter
    def spot_blend(self, val: float):
        self.game_object.blenderObject.data.spot_blend = val

    @property
    def radius(self) -> float:
        return self.game_object.blenderObject.data.shadow_soft_size

    @radius.setter
    def radius(self, val: float):
        self.game_object.blenderObject.data.shadow_soft_size = val


class Light(ULLight):
    _deprecated = False

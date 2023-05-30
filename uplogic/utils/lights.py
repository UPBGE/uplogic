from bge.types import KX_GameObject as GameObject
from bge import logic
from bpy.types import Object
import bpy
from mathutils import Vector, Matrix, Color


def make_unique_light(light: GameObject) -> GameObject:
    '''Make a copy of this light to allow for unique modifications.

    :param `light`: The `KX_LightObject` of which to copy the data.

    :returns: The modified `KX_LightObject`. This return value is for usability reasons and
    is the same as the original argument.
    '''
    lamp = light.blenderObject
    lamp.data = lamp.data.copy()
    return light


class ULLight():
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
        light: GameObject = None
    ) -> None:
        if self._deprecated:
            print('[UPLOGIC] ULLight class will be renamed to "Light" in future releases!')
        if light:
            self.light = make_unique_light(light)
            """The wrapped `KX_LightObject`."""
            return
        game_scene = logic.getCurrentScene()
        scene = bpy.data.scenes[game_scene.name]
        light = bpy.data.lights.new(name, type)
        light = bpy.data.objects.new(name, light)
        scene.collection.objects.link(light)
        self.light = game_scene.convertBlenderObject(light)
        """The wrapped `KX_LightObject`."""
        self.energy = 10

    @property
    def blenderObject(self) -> Object:
        return self.light.blenderObject

    @property
    def energy(self) -> float:
        return self.light.blenderObject.data.energy

    @energy.setter
    def energy(self, val: float):
        self.light.blenderObject.data.energy = val

    @property
    def color(self) -> Color:
        return self.light.blenderObject.data.color

    @color.setter
    def color(self, val: Color):
        self.light.blenderObject.data.color = val

    @property
    def use_shadow(self) -> bool:
        return self.light.blenderObject.data.use_shadow

    @use_shadow.setter
    def use_shadow(self, val: bool):
        self.light.blenderObject.data.use_shadow = val

    @property
    def shadow_clip_start(self) -> float:
        return self.light.blenderObject.data.shadow_buffer_clip_start

    @shadow_clip_start.setter
    def shadow_clip_start(self, val: float):
        self.light.blenderObject.data.shadow_buffer_clip_start = val

    @property
    def shadow_bias(self) -> float:
        return self.light.blenderObject.data.shadow_buffer_bias

    @shadow_bias.setter
    def shadow_bias(self, val: float):
        self.light.blenderObject.data.shadow_buffer_bias = val

    @property
    def use_custom_distance(self) -> bool:
        return self.light.blenderObject.data.use_custom_distance

    @use_custom_distance.setter
    def use_custom_distance(self, val: bool):
        self.light.blenderObject.data.use_custom_distance = val

    @property
    def distance(self) -> float:
        return self.light.blenderObject.data.cutoff_distance

    @distance.setter
    def distance(self, val: float):
        self.light.blenderObject.data.cutoff_distance = val

    @property
    def angle(self)-> float:
        return self.light.blenderObject.data.angle

    @angle.setter
    def angle(self, val: float):
        self.light.blenderObject.data.angle = val

    @property
    def spot_size(self) -> float:
        return self.light.blenderObject.data.spot_size

    @spot_size.setter
    def spot_size(self, val: float):
        self.light.blenderObject.data.spot_size = val

    @property
    def spot_blend(self) -> float:
        return self.light.blenderObject.data.spot_blend

    @spot_blend.setter
    def spot_blend(self, val: float):
        self.light.blenderObject.data.spot_blend = val

    @property
    def radius(self) -> float:
        return self.light.blenderObject.data.shadow_soft_size

    @radius.setter
    def radius(self, val: float):
        self.light.blenderObject.data.shadow_soft_size = val

    @property
    def parent(self) -> GameObject:
        return self.light.parent

    @parent.setter
    def parent(self, val: GameObject):
        self.light.setParent(val)

    def set_parent(self, parent):
        self.light.setParent(parent)

    @property
    def worldPosition(self) -> Vector:
        return self.light.worldPosition

    @worldPosition.setter
    def worldPosition(self, val: Vector):
        self.light.worldPosition = val

    @property
    def localPosition(self) -> Vector:
        return self.light.localPosition

    @localPosition.setter
    def localPosition(self, val: Vector):
        self.light.localPosition = val

    @property
    def worldOrientation(self) -> Matrix:
        return self.light.worldOrientation

    @worldOrientation.setter
    def worldOrientation(self, val: Matrix):
        self.light.worldOrientation = val

    @property
    def localOrientation(self) -> Matrix:
        return self.light.localOrientation

    @localOrientation.setter
    def localOrientation(self, val: Matrix):
        self.light.localOrientation = val

    @property
    def worldScale(self) -> Vector:
        return self.light.worldScale

    @worldScale.setter
    def worldScale(self, val: Vector):
        self.light.worldScale = val

    @property
    def localScale(self) -> Vector:
        return self.light.localScale

    @localScale.setter
    def localScale(self, val: Vector):
        self.light.localScale = val

    @property
    def worldLinearVelocity(self) -> Vector:
        return self.light.worldLinearVelocity

    @worldLinearVelocity.setter
    def worldLinearVelocity(self, val: Vector):
        self.light.worldLinearVelocity = val

    @property
    def localLinearVelocity(self) -> Vector:
        return self.light.localLinearVelocity

    @localLinearVelocity.setter
    def localLinearVelocity(self, val: Vector):
        self.light.localLinearVelocity = val

    @property
    def worldAngularVelocity(self) -> Vector:
        return self.light.worldAngularVelocity

    @worldAngularVelocity.setter
    def worldAngularVelocity(self, val: Vector):
        self.light.worldAngularVelocity = val

    @property
    def localAngularVelocity(self) -> Vector:
        return self.light.localAngularVelocity

    @localAngularVelocity.setter
    def localAngularVelocity(self, val: Vector):
        self.light.localAngularVelocity = val

    @property
    def worldTransform(self) -> Matrix:
        return self.light.worldTransform

    @worldTransform.setter
    def worldTransform(self, val: Matrix):
        self.light.worldTransform = val


class Light(ULLight):
    _deprecated = False

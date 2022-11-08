from bge.types import KX_GameObject as GameObject
from bge import logic
import bpy


def make_unique_light(lamp_ge: GameObject) -> GameObject:
    '''TODO: Documentation
    '''
    lamp = lamp_ge.blenderObject
    lamp.data = lamp.data.copy()
    return lamp_ge


class ULLight():

    def __init__(
        self,
        name: str = '',
        type: str = 'POINT',
        light: GameObject = None
    ) -> None:
        if light:
            self.light = make_unique_light(light)
            return
        game_scene = logic.getCurrentScene()
        scene = bpy.data.scenes[game_scene.name]
        light = bpy.data.lights.new(name, type)
        light = bpy.data.objects.new(name, light)
        scene.collection.objects.link(light)
        self.light = game_scene.convertBlenderObject(light)
        self.energy = 10

    @property
    def energy(self):
        return self.light.blenderObject.data.energy

    @energy.setter
    def energy(self, val):
        self.light.blenderObject.data.energy = val

    @property
    def color(self):
        return self.light.blenderObject.data.color

    @color.setter
    def color(self, val):
        self.light.blenderObject.data.color = val

    @property
    def use_shadow(self):
        return self.light.blenderObject.data.use_shadow

    @use_shadow.setter
    def use_shadow(self, val):
        self.light.blenderObject.data.use_shadow = val

    @property
    def use_custom_distance(self):
        return self.light.blenderObject.data.use_custom_distance

    @use_custom_distance.setter
    def use_custom_distance(self, val):
        self.light.blenderObject.data.use_custom_distance = val

    @property
    def distance(self):
        return self.light.blenderObject.data.cutoff_distance

    @distance.setter
    def distance(self, val):
        self.light.blenderObject.data.cutoff_distance = val

    @property
    def angle(self):
        return self.light.blenderObject.data.angle

    @angle.setter
    def angle(self, val):
        self.light.blenderObject.data.angle = val

    @property
    def spot_size(self):
        return self.light.blenderObject.data.spot_size

    @spot_size.setter
    def spot_size(self, val):
        self.light.blenderObject.data.spot_size = val

    @property
    def spot_blend(self):
        return self.light.blenderObject.data.spot_blend

    @spot_blend.setter
    def spot_blend(self, val):
        self.light.blenderObject.data.spot_blend = val

    @property
    def parent(self):
        return self.light.parent

    @parent.setter
    def parent(self, val):
        self.light.setParent(val)

    @property
    def worldPosition(self):
        return self.light.worldPosition

    @worldPosition.setter
    def worldPosition(self, val):
        self.light.worldPosition = val

    @property
    def localPosition(self):
        return self.light.localPosition

    @localPosition.setter
    def localPosition(self, val):
        self.light.localPosition = val

    @property
    def worldOrientation(self):
        return self.light.worldOrientation

    @worldOrientation.setter
    def worldOrientation(self, val):
        self.light.worldOrientation = val

    @property
    def localOrientation(self):
        return self.light.localOrientation

    @localOrientation.setter
    def localOrientation(self, val):
        self.light.localOrientation = val

    @property
    def worldScale(self):
        return self.light.worldScale

    @worldScale.setter
    def worldScale(self, val):
        self.light.worldScale = val

    @property
    def localScale(self):
        return self.light.localScale

    @localScale.setter
    def localScale(self, val):
        self.light.localScale = val

    @property
    def worldLinearVelocity(self):
        return self.light.worldLinearVelocity

    @worldLinearVelocity.setter
    def worldLinearVelocity(self, val):
        self.light.worldLinearVelocity = val

    @property
    def localLinearVelocity(self):
        return self.light.localLinearVelocity

    @localLinearVelocity.setter
    def localLinearVelocity(self, val):
        self.light.localLinearVelocity = val

    @property
    def worldAngularVelocity(self):
        return self.light.worldAngularVelocity

    @worldAngularVelocity.setter
    def worldAngularVelocity(self, val):
        self.light.worldAngularVelocity = val

    @property
    def localAngularVelocity(self):
        return self.light.localAngularVelocity

    @localAngularVelocity.setter
    def localAngularVelocity(self, val):
        self.light.localAngularVelocity = val

    @property
    def worldTransform(self):
        return self.light.worldTransform

    @worldTransform.setter
    def worldTransform(self, val):
        self.light.worldTransform = val
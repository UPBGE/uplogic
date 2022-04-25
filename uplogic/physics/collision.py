from bge import logic
from bge.types import KX_GameObject as GameObject


class ULCollision():
    """Collision Handler. Not intended for manual use."""
    target = None
    point = None
    normal = None
    tap = False
    consumed = False
    active = False
    _objects = []
    done_objs = []

    def __init__(self, game_object, callback, prop, mat, tap):
        self.callback: function = callback
        self.prop: str = prop
        self.mat: str = mat
        self.tap: bool = tap
        self.game_object: GameObject = game_object
        self.register()

    def collision(self, obj, point, normal):
        if self.tap and self.consumed:
            self.active = True
            return
        self._objects.append(obj)
        material = self.mat
        prop = self.prop
        bo = obj.blenderObject
        if material:
            if material not in [
                slot.material.name for
                slot in
                bo.material_slots
            ]:
                return
        if prop:
            for obj in self._objects:
                if prop not in obj:
                    return

        self.active = True
        if obj not in self.done_objs:
            self.callback(obj, point, normal)
            self.done_objs.append(obj)

    def reset(self):
        self.done_objs = []
        if not self.consumed and self.active:
            self.consumed = True
        elif self.consumed and not self.active:
            self.consumed = False
        self.active = False

    def register(self):
        if self.collision not in self.game_object.collisionCallbacks:
            self.game_object.collisionCallbacks.append(self.collision)
        logic.getCurrentScene().pre_draw.append(self.reset)

    def unregister(self):
        self.game_object.collisionCallbacks.remove(self.collision)
        logic.getCurrentScene().pre_draw.remove(self.reset)


def on_collision(obj, callback, prop='', material='', tap=False) -> ULCollision:
    """Bind a callback to an object's collision detection.

    :param `obj`: Object whose collision detection will be used.
    :param `callback`: Callback to be called when collision occurs. Must have arguments `(obj, point, norma)`.
    :param `prop`: Only look for objects that have this property.
    :param `material`: Only look for objects that have this material applied.
    :param `tap`: Only validate the first frame of the collision.
    """
    return ULCollision(obj, callback, prop, material, tap)

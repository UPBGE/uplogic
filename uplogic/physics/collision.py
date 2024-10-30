from typing import Callable
from bge import logic
from bge.types import KX_GameObject as GameObject
from ..console import error


class Collision():
    """Collision Handler.

    Not intended for manual use."""

    _deprecated = False

    def __init__(
        self,
        game_object: GameObject,
        callback: Callable,
        prop: str = '',
        mat: str = '',
        tap: bool = False,
        post_call: bool = False
    ):
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULCollision class will be renamed to "Collision" in future releases!')
        self.target = None
        self.point = None
        self.normal = None
        self.consumed = False
        self.active = False
        self._objects = []
        self._old_objs = []
        self.callback: Callable = callback
        self.prop: str = prop
        self.mat: str = mat
        self.tap: bool = tap
        self.post_call = post_call
        self.game_object: GameObject = game_object
        self._done_objs = []
        self.register()

    def collision(self, obj, point, normal):
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
            if prop not in obj.getPropertyNames():
                return
            # self.active = True

        self.active = True
        # if self.tap and self.consumed:
        #     return
        if obj not in self._done_objs:
            if (
                self.game_object.collisionGroup & obj.collisionMask and
                self.game_object.collisionMask & obj.collisionGroup and
                not (self.tap and self.consumed)
            ):
                self.callback(obj, point, normal)
            self._done_objs.append(obj)

    def reset(self):
        if self.post_call:
            for obj in self._old_objs:
                if obj not in self._done_objs:
                    self.callback(None, None, None)
        self._old_objs = self._done_objs
        self._done_objs = []
        if not self.consumed and self.active:
            self.consumed = True
        elif self.consumed and not self.active:
            self.consumed = False
        self.active = False

    def register(self):
        if self.collision not in self.game_object.collisionCallbacks:
            self.game_object.collisionCallbacks.append(self.collision)
        logic.getCurrentScene().pre_draw.append(self.reset)

    def remove(self):
        self.game_object.collisionCallbacks.remove(self.collision)
        logic.getCurrentScene().pre_draw.remove(self.reset)


class ULCollision(Collision):
    _deprecated = True


def on_collision(
    obj: GameObject,
    callback: Callable,
    prop: str = '',
    material: str = '',
    tap: bool = False,
    post_call: bool = False
) -> Collision:
    """Bind a callback to an object's collision detection.

    :param `obj`: Object whose collision detection will be monitored.
    :param `callback`: Callback to be called when collision occurs. Must have arguments `(obj, point, normal)`.
    :param `prop`: Only look for objects that have this property.
    :param `material`: Only look for objects that have this material applied.
    :param `tap`: Only validate the first frame of the collision.
    """
    if not isinstance(obj, GameObject):
        error("'on_collision()' Argument 0: Expected 'KX_GameObject' type!")
        return
    return Collision(obj, callback, prop, material, tap, post_call)

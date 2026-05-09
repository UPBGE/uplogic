'''Collision callback utilities for BGE game objects.

Provides the :class:`Collision` handler and the :func:`on_collision` convenience
function for binding per-frame collision callbacks to ``KX_GameObject`` instances.
'''
from typing import Callable
from bge import logic
from bge.types import KX_GameObject as GameObject
from ..console import error


class Collision():
    '''Callback handler for game object collisions.

    Registers itself on the owner object's ``collisionCallbacks`` list and on
    the scene's ``pre_draw`` list so that :meth:`reset` is called once per
    frame to clear per-frame state.

    :param game_object: Object whose collision detection will be monitored.
    :param callback: Callable invoked when a collision is validated.
        Must accept arguments ``(obj, point, normal)``.
    :param prop: When non-empty, only collisions with objects that have this
        game property are forwarded to ``callback``.
    :param mat: When non-empty, only collisions with objects that have this
        material name applied are forwarded to ``callback``.
    :param tap: When ``True``, the callback fires only on the first frame of
        each new collision rather than every frame the objects touch.
    :param post_call: When ``True``, ``callback`` is invoked with
        ``(None, None, None)`` for every object that was colliding last frame
        but is no longer colliding this frame.
    '''

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
        self.point = None
        self.normal = None
        self.target = None
        self.consumed = False
        self.active = False
        self._old_target = None
        self._active = False
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
        '''Internal collision callback registered on ``game_object.collisionCallbacks``.

        Filters the colliding object against the configured ``mat`` and ``prop``
        constraints, then invokes :attr:`callback` when the collision group and
        mask bits match.  Called automatically by the BGE physics system; do not
        call this method directly.

        :param obj: The other game object involved in the collision.
        :param point: World-space contact point of the collision.
        :param normal: World-space contact normal of the collision.
        '''
        if obj in self._objects:
            return
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

        self._objects.append(obj)
        self._active = True
        if obj not in self._old_objs:
            self.consumed = False
        self.target = obj
        self.active = not self.consumed if self.tap else True
        if self.active and obj not in self._done_objs:
            if (
                self.game_object.collisionGroup & obj.collisionMask and
                self.game_object.collisionMask & obj.collisionGroup
            ):
                self.callback(obj, point, normal)
                self.point = point
                self.normal = normal
        self._done_objs.append(obj)

    def reset(self):
        '''Per-frame reset registered on ``scene.pre_draw``.

        Promotes ``_done_objs`` to ``_old_objs``, clears per-frame tracking
        state, and—when :attr:`post_call` is ``True``—fires :attr:`callback`
        with ``(None, None, None)`` for any object that was present last frame
        but absent this frame.  Called automatically by the BGE scene; do not
        call this method directly.
        '''
        if self.post_call:
            for obj in self._old_objs:
                if obj not in self._done_objs:
                    self.callback(None, None, None)

        self.consumed = self._active
        self._active = False
        self.active = False

        self._old_objs = self._done_objs
        self._done_objs = []
        self._objects = []
        self.point = None
        self.normal = None
        self.target = None

    def register(self):
        '''Register :meth:`collision` and :meth:`reset` on the BGE scene hooks.

        Appends :meth:`collision` to ``game_object.collisionCallbacks`` and
        :meth:`reset` to the current scene's ``pre_draw`` list, guarding
        against duplicate registration.
        '''
        if self.collision not in self.game_object.collisionCallbacks:
            self.game_object.collisionCallbacks.append(self.collision)
        if self.reset not in logic.getCurrentScene().pre_draw:
            logic.getCurrentScene().pre_draw.append(self.reset)

    def remove(self):
        '''Unregister this handler from all BGE scene hooks.

        Removes :meth:`collision` from ``game_object.collisionCallbacks`` and
        :meth:`reset` from the current scene's ``pre_draw`` list.  Call this
        when the handler is no longer needed to prevent stale callbacks.
        '''
        self.game_object.collisionCallbacks.remove(self.collision)
        logic.getCurrentScene().pre_draw.remove(self.reset)


class ULCollision(Collision):
    '''[DEPRECATED] Use :class:`Collision` instead.'''
    _deprecated = True


def on_collision(
    obj: GameObject,
    callback: Callable,
    prop: str = '',
    material: str = '',
    tap: bool = False,
    post_call: bool = False
) -> Collision:
    '''Bind a callback to an object's collision detection.

    Convenience wrapper that validates ``obj`` and constructs a
    :class:`Collision` instance.

    :param obj: Object whose collision detection will be monitored.
        Must be a ``KX_GameObject`` instance.
    :param callback: Callable invoked when a collision is validated.
        Must accept arguments ``(obj, point, normal)``.
    :param prop: When non-empty, only collisions with objects that have this
        game property are forwarded to ``callback``.
    :param material: When non-empty, only collisions with objects that have
        this material name applied are forwarded to ``callback``.
    :param tap: When ``True``, the callback fires only on the first frame of
        each new collision.
    :param post_call: When ``True``, ``callback`` is invoked with
        ``(None, None, None)`` for objects that stopped colliding this frame.
    :returns: The registered :class:`Collision` handler, or ``None`` if
        ``obj`` is not a valid ``KX_GameObject``.
    :raises: Logs an error via :func:`uplogic.console.error` when ``obj`` is
        not a ``KX_GameObject``; does not raise an exception.
    '''
    if not isinstance(obj, GameObject):
        error("'on_collision()' Argument 0: Expected 'KX_GameObject' type!")
        return
    return Collision(obj, callback, prop, material, tap, post_call)

'''Character physics controller for BGE kinematic characters.

Wraps the BGE ``KX_CharacterWrapper`` (obtained via ``getCharacter``) and
exposes frame-rate-normalised movement, jump, and velocity helpers through a
clean Python interface.
'''
from bge import logic
from bge.constraints import getCharacter
from bge.types import KX_GameObject as GameObject
from uplogic.utils.constants import FRAMETIME_COMPARE
from mathutils import Vector
import bpy


class Character():
    '''Frame-rate-normalised wrapper around ``KX_CharacterWrapper``.

    Registers a ``pre_draw`` callback so that per-frame derived values
    (``velocity``, ``landed``, ``start_falling``) are updated automatically
    every tick.

    :param owner: The ``KX_GameObject`` that owns the character physics
        controller.
    '''

    _deprecated = False

    def __init__(self, owner: GameObject) -> None:
        '''Initialise the character wrapper for ``owner``.

        Retrieves the ``KX_CharacterWrapper`` via ``getCharacter``, snapshots
        the initial world position, and registers :meth:`reset` on the
        scene's ``pre_draw`` list.

        :param owner: The ``KX_GameObject`` that owns the character physics
            controller.
        '''
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULCharacter class will be renamed to "Character" in future releases!')
        self.owner = owner
        self.wrapper = getCharacter(owner)
        self._old_position = owner.worldPosition.copy()
        self.velocity = Vector((0, 0, 0))
        self.is_walking = False
        self._on_ground = self.wrapper.onGround
        self.landed = False
        self.start_falling = False
        self.speed = 1
        self._phys_step = bpy.data.scenes[logic.getCurrentScene().name].game_settings.physics_step_sub
        logic.getCurrentScene().pre_draw.append(self.reset)

    def reset(self):
        '''Per-frame state update registered on ``scene.pre_draw``.

        Computes ``_velocity`` from the positional delta since the last tick,
        updates the one-frame boolean flags :attr:`landed` and
        :attr:`start_falling`, and zeroes the walk direction when no walk
        input was given this frame.  Called automatically by the BGE scene;
        do not call this method directly.
        '''
        self._velocity = (self.owner.worldPosition - self._old_position) / 10
        self._old_position = self.owner.worldPosition.copy()
        self.landed = not self._on_ground and self.on_ground
        self.start_falling = self._on_ground and not self.on_ground
        self._on_ground = self.on_ground
        if not self.is_walking:
            self.walk = Vector((0, 0, 0))
        self.is_walking = False

    def destroy(self):
        '''Unregister the per-frame :meth:`reset` callback.

        Removes :meth:`reset` from the scene's ``pre_draw`` list.  Call this
        when the character object is removed from the scene to avoid stale
        callbacks.
        '''
        logic.getCurrentScene().pre_draw.remove(self.reset)

    @property
    def on_ground(self) -> bool:
        '''``True`` when the character is resting on a surface.

        Read-only; assignment is silently ignored.  Delegates directly to
        ``wrapper.onGround``.
        '''
        return self.wrapper.onGround

    @on_ground.setter
    def on_ground(self, value):
        # warning('ULCharacter.on_ground is Read-Only!')
        pass

    @property
    def max_jumps(self) -> int:
        '''Maximum number of consecutive jumps allowed before landing.

        Maps to ``wrapper.maxJumps``.
        '''
        return self.wrapper.maxJumps

    @max_jumps.setter
    def max_jumps(self, value):
        self.wrapper.maxJumps = value

    @property
    def gravity(self) -> Vector:
        '''Gravity vector applied to this character controller.

        Maps to ``wrapper.gravity``.
        '''
        return self.wrapper.gravity

    @gravity.setter
    def gravity(self, value):
        self.wrapper.gravity = value

    @property
    def slope(self) -> Vector:
        '''Maximum slope angle the character can walk up without sliding.

        Maps to ``wrapper.maxSlope``.
        '''
        return self.wrapper.maxSlope

    @slope.setter
    def slope(self, value):
        self.wrapper.maxSlope = value

    @property
    def jump_count(self) -> int:
        '''Number of jumps performed since last landing.

        Read-only; assignment is silently ignored.  Maps to
        ``wrapper.jumpCount``.
        '''
        return self.wrapper.jumpCount

    @jump_count.setter
    def jump_count(self, value):
        # warning('Character.jump_count is Read-Only!')
        pass

    @property
    def walk(self) -> Vector:
        '''Frame-rate-normalised walk direction in world space.

        Transforms the physics wrapper's ``walkDirection`` back from the
        wrapper's local space into world space via the owner's
        ``worldOrientation``, then scales by ``_phys_step`` and divides by
        ``speed`` and the current frame-rate factor so that the returned value
        is independent of the actual frame rate.

        :returns: World-space walk direction as a :class:`~mathutils.Vector`,
            normalised for the current frame rate and ``speed``.
        '''
        fps = logic.getAverageFrameRate()
        frametime = 1 / fps if fps > 0 else FRAMETIME_COMPARE
        fps_factor = frametime / FRAMETIME_COMPARE
        return ((self.wrapper.walkDirection @ self.owner.worldOrientation) * self._phys_step) / self.speed / fps_factor

    @walk.setter
    def walk(self, value):
        '''Set the walk direction from a world-space vector.

        Translates ``value`` from world space into the physics wrapper's local
        space via the owner's ``worldOrientation``, then scales by ``speed``
        and the current frame-rate factor before writing to
        ``wrapper.walkDirection``, ensuring consistent movement speed across
        frame rates.

        :param value: Desired walk direction in world space as a
            :class:`~mathutils.Vector`.
        '''
        fps = logic.getAverageFrameRate()
        frametime = 1 / fps if fps > 0 else FRAMETIME_COMPARE
        fps_factor = frametime / FRAMETIME_COMPARE
        self.is_walking = True
        self.wrapper.walkDirection = ((self.owner.worldOrientation @ value) / self._phys_step) * self.speed * fps_factor

    @property
    def velocity(self) -> Vector:
        '''Positional delta computed each tick by :meth:`reset`.

        Represents the distance the character moved since the previous frame,
        scaled by ``1/10``.  Updated once per frame by the ``pre_draw``
        callback; reading between frames returns the value from the last
        completed tick.

        :returns: Per-frame positional delta as a :class:`~mathutils.Vector`.
        '''
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        '''Apply an instantaneous velocity impulse for one physics step.

        Calls ``wrapper.setVelocity`` with the given vector.  This overrides
        the character's current velocity for a single physics step; it does
        not affect the :attr:`velocity` getter, which reflects measured
        positional change.

        :param value: Velocity vector to apply, in world space.
        '''
        self.wrapper.setVelocity(value, 1, False)

    @property
    def jump_force(self) -> float:
        '''Initial upward speed applied when :meth:`jump` is called.

        Maps to ``wrapper.jumpSpeed``.
        '''
        return self.jump_force

    @jump_force.setter
    def jump_force(self, value):
        self.wrapper.jumpSpeed = value

    @property
    def fall_speed(self) -> float:
        '''Maximum downward speed reached during free fall.

        Maps to ``wrapper.fallSpeed``.
        '''
        return self.wrapper.fallSpeed

    @fall_speed.setter
    def fall_speed(self, value):
        self.wrapper.fallSpeed = value

    def move(self, direction=Vector((0, 0, 0)), local=True):
        '''Set the walk direction directly, bypassing frame-rate normalisation.

        Writes to ``wrapper.walkDirection`` immediately, scaling by
        :attr:`speed`.  When ``local`` is ``True`` the direction is first
        rotated into world space via the owner's ``worldOrientation``.

        :param direction: Desired movement direction as a
            :class:`~mathutils.Vector`.  Defaults to no movement.
        :param local: When ``True``, ``direction`` is interpreted in the
            owner's local space and transformed to world space before being
            applied.  When ``False``, ``direction`` is used as-is in world
            space.
        '''
        self.is_walking = True
        self.wrapper.walkDirection = self.owner.worldOrientation @ direction * self.speed if local else direction * self.speed

    def jump(self):
        '''Trigger a jump on the character controller.

        Delegates to ``wrapper.jump()``.  The jump will be executed only if
        the character has remaining jumps available (see :attr:`max_jumps`).
        '''
        self.wrapper.jump()


class ULCharacter(Character):
    '''[DEPRECATED] Use :class:`Character` instead.'''
    _deprecated = True

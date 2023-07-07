from bge import logic
from bge.constraints import getCharacter
from bge.types import KX_GameObject as GameObject
from uplogic.utils.constants import FRAMETIME_COMPARE
# from uplogic.logging import warning
from mathutils import Vector
import bpy


class ULCharacter():
    _deprecated = True

    def __init__(self, owner: GameObject) -> None:
        if self._deprecated:
            print('Warning: ULCharacter class will be renamed to "Character" in future releases!')
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
        self._velocity = (self.owner.worldPosition - self._old_position) / 10
        self._old_position = self.owner.worldPosition.copy()
        self.landed = not self._on_ground and self.on_ground
        self.start_falling = self._on_ground and not self.on_ground
        self._on_ground = self.on_ground
        if not self.is_walking:
            self.walk = Vector((0, 0, 0))
        self.is_walking = False

    def destroy(self):
        logic.getCurrentScene().pre_draw.remove(self.reset)

    @property
    def on_ground(self) -> bool:
        return self.wrapper.onGround

    @on_ground.setter
    def on_ground(self, value):
        # warning('ULCharacter.on_ground is Read-Only!')
        pass

    @property
    def max_jumps(self) -> int:
        return self.wrapper.maxJumps

    @max_jumps.setter
    def max_jumps(self, value):
        self.wrapper.maxJumps = value

    @property
    def gravity(self) -> Vector:
        return self.wrapper.gravity

    @gravity.setter
    def gravity(self, value):
        self.wrapper.gravity = value

    @property
    def slope(self) -> Vector:
        return self.wrapper.maxSlope

    @slope.setter
    def slope(self, value):
        self.wrapper.maxSlope = value

    @property
    def jump_count(self) -> int:
        return self.wrapper.jumpCount

    @jump_count.setter
    def jump_count(self, value):
        # warning('Character.jump_count is Read-Only!')
        pass

    @property
    def walk(self) -> Vector:
        fps = logic.getAverageFrameRate()
        frametime = 1 / fps if fps > 0 else FRAMETIME_COMPARE
        fps_factor = frametime / FRAMETIME_COMPARE
        return ((self.wrapper.walkDirection @ self.owner.worldOrientation) * self._phys_step) / self.speed / fps_factor

    @walk.setter
    def walk(self, value):
        fps = logic.getAverageFrameRate()
        frametime = 1 / fps if fps > 0 else FRAMETIME_COMPARE
        fps_factor = frametime / FRAMETIME_COMPARE
        self.is_walking = True
        self.wrapper.walkDirection = ((self.owner.worldOrientation @ value) / self._phys_step) * self.speed * fps_factor

    @property
    def velocity(self) -> Vector:
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self.wrapper.setVelocity(value, 1, False)

    @property
    def jump_force(self) -> float:
        return self.jump_force

    @jump_force.setter
    def jump_force(self, value):
        self.wrapper.jumpSpeed = value

    @property
    def fall_speed(self) -> float:
        return self.wrapper.fallSpeed

    @fall_speed.setter
    def fall_speed(self, value):
        self.wrapper.fallSpeed = value

    def move(self, direction=Vector((0, 0, 0)), local=True):
        self.is_walking = True
        self.wrapper.walkDirection = self.owner.worldOrientation @ direction * self.speed if local else direction * self.speed

    def jump(self):
        self.wrapper.jump()


class Character(ULCharacter):
    _deprecated = False

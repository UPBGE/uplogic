from bge import logic
from bge.constraints import getCharacter
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.utils import debug
import bpy


class ULCharacter():
    def __init__(self, owner: GameObject) -> None:
        self.owner = owner
        self.character = getCharacter(owner)
        self._old_position = owner.worldPosition.copy()
        self.velocity = Vector((0, 0, 0))
        self.is_walking = False
        self._phys_step = bpy.data.scenes[logic.getCurrentScene().name].game_settings.physics_step_sub
        logic.getCurrentScene().pre_draw.append(self.reset)

    def reset(self):
        self._velocity = (self.owner.worldPosition - self._old_position) / 10
        self._old_position = self.owner.worldPosition.copy()
        if not self.is_walking:
            self.walk = Vector((0, 0, 0))
        self.is_walking = False

    def destroy(self):
        logic.getCurrentScene().pre_draw.remove(self.reset)

    @property
    def on_ground(self):
        return self.character.onGround

    @on_ground.setter
    def on_ground(self, value):
        debug('Character.on_ground is Read-Only!')

    @property
    def max_jumps(self):
        return self.character.maxJumps

    @max_jumps.setter
    def max_jumps(self, value):
        self.character.maxJumps = value

    @property
    def gravity(self):
        return self.character.gravity

    @gravity.setter
    def gravity(self, value):
        self.character.gravity = value

    @property
    def jump_count(self):
        return self.character.jumpCount

    @jump_count.setter
    def jump_count(self, value):
        debug('Character.jump_count is Read-Only!')

    @property
    def walk(self):
        return (self.character.walkDirection @ self.owner.worldOrientation) * self._phys_step

    @walk.setter
    def walk(self, value):
        self.is_walking = True
        self.character.walkDirection = (self.owner.worldOrientation @ value) / self._phys_step

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self.character.setVelocity(value, 1, False)

    @property
    def jump_force(self):
        return self.jump_force

    @jump_force.setter
    def jump_force(self, value):
        self.character.jumpSpeed = value

    @property
    def fall_speed(self):
        return self.character.fallSpeed

    @fall_speed.setter
    def fall_speed(self, value):
        self.character.fallSpeed = value

    def move(self, direction=Vector((0, 0, 0)), local=True):
        self.is_walking = True
        self.character.walkDirection = self.owner.worldOrientation @ direction if local else direction

    def jump(self):
        self.character.jump()

from bge import constraints
from bge import logic
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
import bpy


class ULCharacterInfo(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.max_jumps = None
        self.cur_jump = None
        self.gravity = None
        self.walk_dir = None
        self.on_ground = None
        self.local = False
        self.MAX_JUMPS = ULOutSocket(self, self.get_max_jumps)
        self.CUR_JUMP = ULOutSocket(self, self.get_current_jump)
        self.GRAVITY = ULOutSocket(self, self.get_gravity)
        self.WALKDIR = ULOutSocket(self, self.get_walk_dir)
        self.ON_GROUND = ULOutSocket(self, self.get_on_ground)

    def get_max_jumps(self):
        return self.physics.maxJumps

    def get_current_jump(self):
        return self.physics.jumpCount

    def get_gravity(self):
        return self.physics.gravity

    def get_walk_dir(self):
        physics = self.physics
        wdir = (
            physics.walkDirection @ self.owner.worldOrientation
            if self.local else
            physics.walkDirection
        )
        return wdir * bpy.data.scenes[
            logic.getCurrentScene().name
        ].game_settings.physics_step_sub

    def get_on_ground(self):
        return self.physics.onGround

    def evaluate(self):
        game_object = self.owner = self.get_input(self.game_object)
        self.physics = constraints.getCharacter(game_object)

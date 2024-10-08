from bge import constraints
from bge import logic
from mathutils import Vector
from uplogic.nodes import ULActionNode
import bpy


class ULSetCharacterWalkDir(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.walkDir = None
        self.local = False
        self.active = False
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            if self.active:
                game_object = self.get_input(self.game_object)
                physics = constraints.getCharacter(game_object)
                physics.walkDirection = Vector((0, 0, 0))
                self.active = False
            return
        elif not self.active:
            self.active = True
        game_object = self.get_input(self.game_object)
        local = self.local
        walkDir = self.get_input(self.walkDir)
        if local:
            walkDir = game_object.worldOrientation @ walkDir
        physics = constraints.getCharacter(game_object)
        physics.walkDirection = (
            walkDir /
            bpy.data.scenes[
                logic.getCurrentScene().name
            ].game_settings.physics_step_sub
        )
        self._done = True

from bge.types import KX_GameObject
from uplogic.nodes import ULConditionNode
from uplogic.physics.collision import Collision
from uplogic.nodes import ULLogicContainer
from bpy.types import Material
from mathutils import Vector


class ULCollision(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.game_object = None
        self.use_mat = False
        self.prop = ''
        self.material = ''
        self.pulse = False
        self._collision = None
        self._active = None
        self._point = None
        self._normal = None
        self._target = None
        self._objects = None

        # self._target = None
        # self._point = None
        # self._normal = None
        # self._collision_triggered = False
        # self._consumed = False
        # self._game_object = None
        # self._objects = []

        self.COLLISION = self.add_output(self.get_collision)
        self.TARGET = self.add_output(self.get_target)
        self.POINT = self.add_output(self.get_point)
        self.NORMAL = self.add_output(self.get_normal)
        self.OBJECTS = self.add_output(self.get_objects)
        
    def get_collision(self):
        return self._collision.active

    def get_point(self):
        return self._collision.point

    def get_normal(self):
        return self._collision.normal

    def get_target(self):
        return self._collision.target

    def get_objects(self):
        return self._collision._objects

    def on_collision(self, obj, point, normal):
        pass

    def evaluate(self):
        game_obj = self.get_input(self.game_object)
        if self._collision is None or self._collision.game_object is not game_obj:
            self._collision = Collision(
                game_obj,
                self.on_collision,
                self.get_input(self.prop),
                self.get_input(self.material),
                not self.get_input(self.pulse),
                True
            )

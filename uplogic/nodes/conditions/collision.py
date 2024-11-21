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
        # print(self._collision, '########')
        return self._collision.target

    def get_objects(self):
        return self._collision._objects

    def on_collision(self, obj, point, normal):
    #     self._active = self._collision.active
    #     self._point = point
    #     self._normal = normal
    #     self._target = obj
    #     self._objects = self._collision._objects
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
        
        
    # def _collision_callback(self, obj: KX_GameObject, point: Vector, normal: Vector):
    #     self._objects.append(obj)
    #     use_mat = self.get_input(self.use_mat)
    #     if use_mat:
    #         material: Material = self.get_input(self.material)
    #         if material:
    #             for obj in self._objects:
    #                 bo = obj.blenderObject
    #                 if material.name not in [
    #                     slot.material.name for
    #                     slot in
    #                     bo.material_slots
    #                 ]:
    #                     self._objects.remove(obj)
    #                 else:
    #                     self._collision_triggered = True
    #                     self._target = obj
    #                     self._point = point
    #                     self._normal = normal
    #                     return
    #             self._collision_triggered = False
    #             return
    #     else:
    #         prop = self.get_input(self.prop)
    #         if prop:
    #             for obj in self._objects:
    #                 if prop not in obj:
    #                     self._objects.remove(obj)
    #                 else:
    #                     self._collision_triggered = True
    #                     self._target = obj
    #                     self._point = point
    #                     self._normal = normal
    #                     return
    #             self._collision_triggered = False
    #             return
    #     self._collision_triggered = True
    #     self._target = obj
    #     self._point = point
    #     self._normal = normal

    # def reset(self):
    #     super().reset()
    #     self._collision_triggered = False
    #     self._objects = []

    # def _reset_game_object(self, game_object: KX_GameObject):
    #     if self._game_object:
    #         self._game_object.collisionCallbacks.remove(
    #             self._collision_callback
    #         )
    #     game_object.collisionCallbacks.append(
    #         self._collision_callback
    #     )
    #     self._game_object = game_object
    #     self._collision = False
    #     self._target = None
    #     self._point = None
    #     self._normal = None
    #     self._collision_triggered = False

    # def evaluate(self):
    #     last_target = self._target
    #     game_object = self.get_input(self.game_object)
    #     if game_object is not self._game_object:
    #         self._reset_game_object(game_object)
    #     collision = self._collision_triggered
    #     if last_target is not self._target:
    #         self._consumed = False
    #     if collision and not self.pulse:
    #         self._collision = collision and not self._consumed
    #         self._consumed = True
    #     elif self.pulse:
    #         self._collision = collision
    #     else:
    #         self._consumed = False
    #         self._collision = False

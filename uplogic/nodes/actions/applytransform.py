from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULApplyTransform(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.vec1 = None
        self.vec2 = None
        self.vec3 = None
        self.local = False
        self.done = None
        self.mode = 0
        self._actions = [
            self.apply_movement,
            self.apply_rotation,
            self.apply_force,
            self.apply_torque,
            self.apply_impulse,
        ]
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def apply_movement(self, obj, local):
        obj.applyMovement(self.get_input(self.vec1), local)

    def apply_rotation(self, obj, local):
        obj.applyRotation(self.get_input(self.vec3), local)

    def apply_force(self, obj, local):
        obj.applyForce(self.get_input(self.vec1), local)

    def apply_torque(self, obj, local):
        obj.applyTorque(self.get_input(self.vec1), local)

    def apply_impulse(self, obj, local):
        obj.applyImpulse(self.get_input(self.vec1), self.get_input(self.vec2), local)

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        local = self.local
        self._actions[self.mode](game_object, local)
        self.done = True

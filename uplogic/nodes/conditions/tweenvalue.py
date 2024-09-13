from uplogic.nodes import ULConditionNode
from uplogic.utils.math import clamp
from uplogic.utils.math import interpolate
from mathutils import Vector


class TweenValueNode(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.forward = False
        self.back = False
        self.from_float = 0.0
        self.to_float = 1.0
        self.from_vec = Vector((0, 0, 0))
        self.to_vec = Vector((1, 1, 1))
        self.duration = 1.0

        self._time = 0.0

        self.mapping = None
        self.active = False

        self.on_demand = True
        self.instant_reset = False
        self.value_type = 0  # 0 -> float, 1 -> Vector

        self._result = 0.0
        self._factor = 0.
        self._eval = 0.

        self._direction = 1

        self.DONE = self.add_output(self.get_done)
        self.REACHED = self.add_output(self.get_reached)
        self.RESULT_FLOAT = self.add_output(self.get_float)
        self.RESULT_VEC = self.add_output(self.get_vec)
        self.FAC = self.add_output(self.get_fac)

    def get_done(self):
        return self._done

    def get_reached(self):
        return self._factor == self._direction

    def get_fac(self):
        return self._factor

    def get_vec(self):
        self.active = True
        if self.on_demand:
            self.forward = True
            self.back = False
        self._result = self.get_input(self.from_vec).lerp(self.get_input(self.to_vec), self._eval)
        return self._result

    def get_float(self):
        self.active = True
        if self.on_demand:
            self.forward = True
            self.back = False
        self._result = interpolate(self.get_input(self.from_float), self.get_input(self.to_float), self._eval)
        return self._result

    def reset(self):
        self.active = False
        return super().reset()

    def evaluate(self):
        forward = self.get_condition(self.forward)
        
        back = self.get_condition(self.back)
        if not forward and not back:
            return
        self.active = True
        if not self.active and not self.on_demand:
            return
        duration = self.get_input(self.duration)
        mapping = self.mapping.curve
        if forward:
            self._direction = 1
            if duration > 0:
                self._time = clamp(self._time + self.network.time_per_frame, 0, duration)
                self._factor = self._time / duration
            else:
                self._factor = 1
            self._eval = clamp(mapping.evaluate(
                mapping.curves[0],
                self._factor
            ))
        elif back:
            self._direction = 0
            if self.on_demand and self.instant_reset:
                duration = 0
                self._time = 0.0
            if duration > 0:
                self._time = clamp(self._time - self.network.time_per_frame, 0, duration)
                self._factor = self._time / duration
            else:
                self._factor = 0
            self._eval = clamp(mapping.evaluate(
                mapping.curves[0],
                self._factor
            ))
        self.active = False
        if self.on_demand:
            self.forward = False
            self.back = True
        self._done = True

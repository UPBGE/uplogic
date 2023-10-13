from bge import logic, types
from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector


class ULGamepadSticks(ULParameterNode):
    def __init__(self, axis=0):
        ULParameterNode.__init__(self)
        self.axis = axis
        self.inverted = None
        self.index = None
        self.sensitivity = None
        self.threshold = None
        self._x_axis_values = None
        self._y_axis_values = None
        self._sensitivity = 0.0
        self.raw_values = [0, 0]
        self.VEC = ULOutSocket(self, self.get_vec)
        self.X = ULOutSocket(self, self.get_x_axis)
        self.Y = ULOutSocket(self, self.get_y_axis)

    def get_vec(self):
        return Vector((self.get_x_axis(), self.get_y_axis(), 0))

    def get_x_axis(self):
        x = self.raw_values[0]
        if -self.threshold < x < self.threshold:
            x = 0
        return x * self._sensitivity

    def get_y_axis(self):
        y = -self.raw_values[1]
        if -self.threshold < y < self.threshold:
            y = 0
        return y * self._sensitivity

    def evaluate(self):
        index = self.get_input(self.index)

        if logic.joysticks[index]:
            joystick: types.SCA_PythonJoystick = logic.joysticks[index]
        else:
            self._x_axis_values = 0
            self._y_axis_values = 0
            return
        axis = self.get_input(self.axis)
        raw_values = joystick.axisValues
        if axis == 0:
            self.raw_values = [raw_values[0], raw_values[1]]
        elif axis == 1:
            self.raw_values = [raw_values[2], raw_values[3]]
        inverted = self.get_input(self.inverted)
        sensitivity = self.get_input(self.sensitivity)
        self._sensitivity = -sensitivity if inverted else sensitivity
        self.threshold = self.get_input(self.threshold)

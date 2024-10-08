from bge import logic, types
from uplogic.nodes import ULParameterNode
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
        self.VEC = self.add_output(self.get_vec)
        self.X = self.add_output(self.get_x_axis)
        self.Y = self.add_output(self.get_y_axis)

    def get_vec(self):
        self.fetched = True
        inverted = self.get_input(self.inverted)
        x = self.get_x_axis()
        y = self.get_y_axis()
        return Vector((
            -x if inverted[0] else x,
            -y if inverted[1] else y
        ))

    def get_x_axis(self):
        self.fetched = True
        x = self.raw_values[0]
        if -self.threshold < x < self.threshold:
            x = 0
        return x * self._sensitivity

    def get_y_axis(self):
        self.fetched = True
        y = -self.raw_values[1]
        if -self.threshold < y < self.threshold:
            y = 0
        return y * self._sensitivity

    def fetch(self):
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
        self._sensitivity = self.get_input(self.sensitivity)
        self.threshold = self.get_input(self.threshold)

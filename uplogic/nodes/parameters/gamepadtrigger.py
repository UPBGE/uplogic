from bge import logic
from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector


class ULGamepadTrigger(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.index = None
        self.sensitivity = None
        self.threshold = None
        self._values = None
        self.LEFT = ULOutSocket(self, self.get_left)
        self.RIGHT = ULOutSocket(self, self.get_right)

    @property
    def values(self) -> Vector:
        if self._values is not None:
            return self._values
        index = self.get_input(self.index)
        sensitivity = self.get_input(self.sensitivity)
        if logic.joysticks[index]:
            joystick = logic.joysticks[index]
        else:
            self._values = Vector((0, 0))
            return self._values
        self._values = Vector((
            joystick.axisValues[4] * sensitivity,
            joystick.axisValues[5] * sensitivity
        ))
        return self._values

    def get_left(self):
        threshold = self.get_input(self.threshold)
        value = self.values.x
        if -threshold < value < threshold:
            value = 0
        return value

    def get_right(self):
        threshold = self.get_input(self.threshold)
        value = self.values.y
        if -threshold < value < threshold:
            value = 0
        return value

    def reset(self):
        super().reset()
        self._values = None

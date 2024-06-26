from uplogic.nodes import ULParameterNode
from uplogic.utils.math import rotate2d
from uplogic.utils.math import rotate3d
from uplogic.utils.math import rotate_by_axis
from uplogic.utils.math import rotate_by_euler
from mathutils import Vector
from math import degrees


class ULRotateByPoint(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        # self.mode = 0
        self.global_axis = 0
        self.origin = None
        self.pivot = None
        self.angle = None
        self.arbitrary_axis = None
        self.euler_angles = None
        self.OUT = self.add_output(self.get_point)
        self._operations = [
            self._rotate2d,
            self._rotate3d,
            self._rotate_by_axis,
            self._rotate_by_euler
        ]

    @property
    def mode(self):
        return None

    @mode.setter
    def mode(self, val):
        self.OUT._value_getter = self._operations[val]

    def _rotate2d(self):
        return rotate2d(
            self.get_input(self.origin),
            self.get_input(self.pivot),
            degrees(self.get_input(self.angle))
        )

    def _rotate3d(self):
        return rotate3d(
            self.get_input(self.origin),
            self.get_input(self.pivot),
            degrees(self.get_input(self.angle)),
            self.global_axis
        )

    def _rotate_by_axis(self):
        return rotate_by_axis(
            self.get_input(self.origin),
            self.get_input(self.pivot),
            degrees(self.get_input(self.angle)),
            self.get_input(self.arbitrary_axis)
        )

    def _rotate_by_euler(self):
        return rotate_by_euler(
            self.get_input(self.origin),
            self.get_input(self.pivot),
            self.get_input(self.euler_angles)
        )

    def get_point(self):
        return Vector((0, 0, 0))

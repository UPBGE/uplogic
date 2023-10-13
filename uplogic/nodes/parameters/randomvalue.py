from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from random import randint
from random import random
from random import uniform
from mathutils import Vector


class ULRandomValue(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.min_float = None
        self.max_float = None
        self.min_int = None
        self.max_int = None
        self.min_vector = None
        self.max_vector = None
        self.probability = None
        self.seed = None
        self.OUT = ULOutSocket(self, self.get_float)

        self.getters = [
            self.get_float,
            self.get_integer,
            self.get_vector,
            self.get_bool
        ]

        self.data_type = 0

    @property
    def data_type(self):
        return None

    @data_type.setter
    def data_type(self, val):
        self.OUT._value_getter = self.getters[val]

    def get_float(self):
        return uniform(
            self.get_input(self.min_float),
            self.get_input(self.max_float)
        )

    def get_integer(self):
        return randint(
            self.get_input(self.min_int),
            self.get_input(self.max_int)
        )

    def get_vector(self):
        vec1 = self.get_input(self.min_vector)
        vec2 = self.get_input(self.max_vector)
        if not(isinstance(vec1, Vector) and isinstance(vec2, Vector)):
            return Vector((0, 0, 0))
        vec = Vector((
            uniform(vec1.x, vec2.x),
            uniform(vec1.y, vec2.y),
            uniform(vec1.z, vec2.z)
        ))
        return vec

    def get_bool(self):
        return random() <= self.get_input(self.probability)

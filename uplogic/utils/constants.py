import operator
from mathutils import Vector
from bge import logic


# uplogic game properties
VEHICLE = '.ulvehicleconst'
SHIP = '.ulshipconst'
FLOTSAM = '.ulflotsamconst'
WATER = '.ulwater'

STREAMTYPE_DOWNSTREAM = 0
STREAMTYPE_UPSTREAM = 1

DISCONNECT_MSG = '!DISCONNECT'


LOGIC_OPERATORS = [
    operator.eq,
    operator.ne,
    operator.gt,
    operator.lt,
    operator.ge,
    operator.le
]


def MATMUL (a, b):
    return a @ b


OPERATORS = {
    "ADD": operator.add,
    "DIV": operator.truediv,
    "MUL": operator.mul,
    "SUB": operator.sub,
    'FDIV': operator.floordiv,
    'MATMUL': MATMUL,#operator.matmul,
    'MOD': operator.mod,
    'POW': operator.pow
}


LO_AXIS_TO_STRING_CODE = {
    0: "X", 1: "Y", 2: "Z",
    3: "-X", 4: "-Y", 5: "-Z",
}


LO_AXIS_TO_VECTOR = {
    0: Vector((1, 0, 0)), 1: Vector((0, 1, 0)),
    2: Vector((0, 0, 1)), 3: Vector((-1, 0, 0)),
    4: Vector((0, -1, 0)), 5: Vector((0, 0, -1)),
}

FRONT_AXIS_VECTOR_SIGNED = {
    0: Vector((1, 0)), 1: Vector((1, 0)),
    2: Vector((0, 1)), 3: Vector((-1, 0)),
    4: Vector((-1, 0)), 5: Vector((0, -1)),
}


FRAMETIME_COMPARE = 1 / 60


def FPS_FACTOR() -> float:
    avg = logic.getAverageFrameRate()
    return (60 / avg) if 0 < avg < 10000 else 1


RED = [1, 0, 0]
GREEN = [0, 1, 0]
BLUE = [0, 0, 1]
YELLOW = [1, 1, 0]
PURPLE = [1, 0, 1]
TORQUISE = [0, 1, 1]
WHITE = [1, 1, 1]
BLACK = [0, 0, 0]
GREY = [.5, .5, .5]

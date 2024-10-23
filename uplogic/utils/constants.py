import operator
from mathutils import Vector
from bge import logic
import math
from .math import matmul
from .math import multadd
from .math import isqrt
from .math import smin
from .math import smax
from .math import sign
from .math import compare
from .math import fraction
from .math import trunc_mod
from .math import floor_mod
from .math import wrap
from .math import snap
from .math import ping_pong
from .math import _round
from .math import _log
from .math import _min
from .math import _max
from .math import _asin
from .math import _acos
from .math import _atan
from .math import _lerp
import bpy


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

OPERATORS = {
    "ADD": operator.add,
    "DIV": operator.truediv,
    "MUL": operator.mul,
    "SUB": operator.sub,
    'FDIV': operator.floordiv,
    'MATMUL': matmul, #operator.matmul,
    'MOD': operator.mod,
    'POW': operator.pow
}

MATH_OPERATORS = [
    operator.add,  # 0
    operator.sub,  # 1
    operator.mul,  # 2
    operator.truediv,  # 3
    multadd,  # 4
    operator.mod,  # 5
    operator.floordiv,  # 6
    operator.pow,  # 7
    _log,  # 8
    math.sqrt,  # 9
    isqrt,  # 10
    abs,  # 11
    math.exp,  # 12
    _min,  # 13
    _max,  # 14
    operator.lt,  # 15
    operator.gt,  # 16
    sign,  # 17
    compare,  # 18
    smin,  # 19
    smax,  # 20
    _round,  # 21
    math.floor,  # 22
    math.ceil,  # 23
    math.trunc,  # 24
    fraction,  # 25
    trunc_mod,  # 26
    floor_mod,  # 27
    wrap,  # 28
    snap,  # 29
    ping_pong,  # 30
    math.sin,  # 31
    math.cos,  # 32
    math.tan,  # 33
    _asin,  # 34
    _acos,  # 35
    _atan,  # 36
    math.atan2,  # 37
    math.sinh,  # 38
    math.cosh,  # 39
    math.tanh,  # 40
    math.radians,  # 41
    math.degrees,  # 42
    _lerp  # 43
]


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


FRAMETIME_COMPARE = 1 / bpy.data.scenes[logic.getCurrentScene().name].render.fps


def FPS_FACTOR() -> float:
    avg = logic.getAverageFrameRate()
    return (bpy.data.scenes[logic.getCurrentScene().name].game_settings.fps / avg) if 0 < avg < 10000 else 1

def DELTA_TIME() -> float:
    avg = logic.getAverageFrameRate()
    return (1 / avg) if 0 < avg < 10000 else 0.0


RED = [1, 0, 0, 1]
GREEN = [0, 1, 0, 1]
BLUE = [0, 0, 1, 1]
YELLOW = [1, 1, 0, 1]
PURPLE = [1, 0, 1, 1]
TORQUISE = [0, 1, 1, 1]
WHITE = [1, 1, 1, 1]
BLACK = [0, 0, 0, 1]
GREY = [.5, .5, .5, 1]

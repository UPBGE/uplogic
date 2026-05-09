'''Compile-time constants, operator tables, and per-frame timing helpers for uplogic.
'''
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
'''Internal game-property key used to tag BGE objects as vehicles.'''

SHIP = '.ulshipconst'
'''Internal game-property key used to tag BGE objects as ships.'''

FLOTSAM = '.ulflotsamconst'
'''Internal game-property key used to tag BGE objects as flotsam.'''

WATER = '.ulwater'
'''Internal game-property key used to tag BGE objects as water surfaces.'''

STREAMTYPE_DOWNSTREAM = 0
'''Stream direction flag indicating downstream (outgoing) network data.'''

STREAMTYPE_UPSTREAM = 1
'''Stream direction flag indicating upstream (incoming) network data.'''

DISCONNECT_MSG = '!DISCONNECT'
'''Sentinel string transmitted over the network to signal a disconnect event.'''


LOGIC_OPERATORS = [
    operator.eq,
    operator.ne,
    operator.gt,
    operator.lt,
    operator.ge,
    operator.le
]
'''List of comparison operator functions in the order ``eq, ne, gt, lt, ge, le``.

Used by the logic-node system to evaluate conditions by index.
'''

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
'''Dict mapping operator name strings to binary operator functions.

Keys include ``"ADD"``, ``"DIV"``, ``"MUL"``, ``"SUB"``, ``"FDIV"``,
``"MATMUL"``, ``"MOD"``, and ``"POW"``.
'''

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
'''Indexed list of math/operator functions used by the logic-node math system.

Indices 0–43 map to specific operations. Retrieve a function by its integer
index when building logic-node math pipelines.
'''


LO_AXIS_TO_STRING_CODE = {
    0: "X", 1: "Y", 2: "Z",
    3: "-X", 4: "-Y", 5: "-Z",
}
'''Dict mapping axis integer codes ``0``–``5`` to string labels.

``0`` → ``"X"``, ``1`` → ``"Y"``, ``2`` → ``"Z"``,
``3`` → ``"-X"``, ``4`` → ``"-Y"``, ``5`` → ``"-Z"``.
'''


LO_AXIS_TO_VECTOR = {
    0: Vector((1, 0, 0)), 1: Vector((0, 1, 0)),
    2: Vector((0, 0, 1)), 3: Vector((-1, 0, 0)),
    4: Vector((0, -1, 0)), 5: Vector((0, 0, -1)),
}
'''Dict mapping axis codes ``0``–``5`` to unit ``Vector`` instances.

Each entry is the 3-D unit vector aligned with the corresponding axis.
'''

FRONT_AXIS_VECTOR_SIGNED = {
    0: Vector((1, 0)), 1: Vector((1, 0)),
    2: Vector((0, 1)), 3: Vector((-1, 0)),
    4: Vector((-1, 0)), 5: Vector((0, -1)),
}
'''Dict mapping axis codes to 2-D signed front vectors.

Used when a signed planar direction is needed for a given axis code.
'''


FRAMETIME_COMPARE = 1 / bpy.data.scenes[logic.getCurrentScene().name].render.fps
'''Expected frame time in seconds (``1 / scene_fps``) computed at module load time.

Used as a baseline for frame-rate comparisons.
'''


def FPS_FACTOR() -> float:
    '''Return the current frames-per-second scaling factor.

    Computes the ratio of the scene's target FPS to the current average FPS
    so that per-frame values can be scaled to remain independent of actual
    frame rate. Returns ``1`` when the average FPS is outside the valid range
    ``(0, 10000)``.

    :returns: ``scene_fps / avg_fps`` as a ``float``, or ``1`` when FPS is
        out of the valid range.
    '''
    avg = logic.getAverageFrameRate()
    return (bpy.data.scenes[logic.getCurrentScene().name].game_settings.fps / avg) if 0 < avg < 10000 else 1

def DELTA_TIME() -> float:
    '''Return the current frame delta time in seconds.

    Computes ``1 / avg_fps`` for the current average frame rate. Returns
    ``0.0`` when the average FPS is outside the valid range ``(0, 10000)``.

    :returns: Frame delta time as a ``float``, or ``0.0`` when FPS is out of
        the valid range.
    '''
    avg = logic.getAverageFrameRate()
    return (1 / avg) if 0 < avg < 10000 else 0.0


RED = [1, 0, 0, 1]
'''RGBA colour list for red — used in debug rendering.'''

GREEN = [0, 1, 0, 1]
'''RGBA colour list for green — used in debug rendering.'''

BLUE = [0, 0, 1, 1]
'''RGBA colour list for blue — used in debug rendering.'''

YELLOW = [1, 1, 0, 1]
'''RGBA colour list for yellow — used in debug rendering.'''

PURPLE = [1, 0, 1, 1]
'''RGBA colour list for purple — used in debug rendering.'''

TORQUISE = [0, 1, 1, 1]
'''RGBA colour list for turquoise — used in debug rendering.'''

WHITE = [1, 1, 1, 1]
'''RGBA colour list for white — used in debug rendering.'''

BLACK = [0, 0, 0, 1]
'''RGBA colour list for black — used in debug rendering.'''

GREY = [.5, .5, .5, 1]
'''RGBA colour list for grey — used in debug rendering.'''

ORANGE = [1, .5, .0, 1]
'''RGBA colour list for orange — used in debug rendering.'''


class prop_type_invalid:
    '''Sentinel class representing an invalid game-property type.'''
    ...


PROP_TYPE_INVALID = prop_type_invalid
'''Sentinel instance used to represent an invalid game-property type.'''

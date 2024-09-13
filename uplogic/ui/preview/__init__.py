from ..widget import Widget
from .canvas import Canvas
from .layout import FloatLayout, RelativeLayout, GridLayout, BoxLayout, PolarLayout
import math
from mathutils import Vector

def rotate2d(origin, pivot, angle):
    angle = math.radians(angle)
    return Vector((
        ((origin[0] - pivot[0]) * math.cos(angle)) - ((origin[1] - pivot[1]) * math.sin(angle)) + pivot[0],
        ((origin[0] - pivot[0]) * math.sin(angle)) + ((origin[1] - pivot[1]) * math.cos(angle)) + pivot[1]
    ))
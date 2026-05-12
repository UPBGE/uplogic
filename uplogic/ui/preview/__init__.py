'''Blender-editor (bpy) variants of the uplogic UI widget system.

These widgets render inside a Blender ``VIEW_3D`` editor region using
``SpaceView3D.draw_handler_add`` rather than the BGE ``post_draw`` hook.
They share the same :class:`~uplogic.ui.widget.Widget` base class and GPU
shader pipeline as the runtime widgets.

Typical usage::

    from uplogic.ui.preview import Canvas
    canvas = Canvas()
    canvas.register()          # attach to the 3-D viewport draw handler
'''
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
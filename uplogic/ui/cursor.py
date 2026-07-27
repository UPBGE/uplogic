'''Custom mouse cursor widget for uplogic UI.

:func:`set_custom_cursor` creates a :class:`Cursor` sprite that tracks the
mouse position and draws itself via a ``post_draw`` hook, replacing the
system cursor visually.
'''

from .image import Sprite
from uplogic.input import MOUSE
import gpu
import bge, bpy
from gpu_extras.batch import batch_for_shader
from bge import logic, render
from math import ceil, floor
from mathutils import Vector


CURSOR = None


def remove_custom_cursor():
    '''Remove all active custom cursor draw handlers from the current scene.

    Scans ``scene.post_draw`` and removes every function named
    ``_draw_custom_cursor``.
    '''
    scene = bge.logic.getCurrentScene()
    to_remove = []
    for f in scene.post_draw:
        if f.__name__ == '_draw_custom_cursor':
            to_remove.append(f)
    for f in to_remove:
        scene.post_draw.remove(f)


def set_custom_cursor(texture=None, size=(30,30), offset=(0, 0), rows=1, cols=1, idx=0):
    '''Create and return a :class:`Cursor` sprite widget.

    Any previously registered custom cursor is removed first.

    :param texture: Image file path for the cursor sprite.
    :param size: Pixel dimensions ``(width, height)`` of the cursor.
    :param offset: Pixel offset ``(x, y)`` applied to the cursor position.
    :param rows: Number of rows in the sprite sheet.
    :param cols: Number of columns in the sprite sheet.
    :param idx: Initial sprite sheet cell index.
    :returns: The newly created :class:`Cursor`.
    '''
    return Cursor(texture=texture, size=size, offset=offset, rows=rows, cols=cols, idx=idx)


class Cursor(Sprite):
    '''Sprite widget that tracks the mouse position and draws as a custom cursor.

    Registers a ``_draw_custom_cursor`` handler in ``scene.post_draw`` on
    construction so it is drawn every frame without being attached to a
    :class:`~uplogic.ui.canvas.Canvas`.  Any previously registered cursor
    handler is removed first.

    :param texture: Image file path for the cursor sprite.
    :param size: Pixel dimensions ``(width, height)``.
    :param offset: Pixel offset ``(x, y)`` from the mouse position.
    :param rows: Sprite sheet row count.
    :param cols: Sprite sheet column count.
    :param idx: Initial sprite sheet cell index.
    '''

    def __init__(self, texture=None, size=(30,30), offset=(0, 0), rows=1, cols=1, idx=0):
        self.offset = offset
        self._idx = idx
        self._texture = None
        super().__init__(MOUSE.position, size, texture=texture, cols=cols, rows=rows, idx=idx)
        remove_custom_cursor()
        self._shader = None
        # self.texture = texture
        self.pos = MOUSE.position
        bge.logic.getCurrentScene().post_draw.append(self._draw_custom_cursor)
        self.start()

    @property
    def _draw_pos(self):
        return Vector((
            floor(self.pos[0] * render.getWindowWidth()),
            floor((1 - self.pos[1]) * render.getWindowHeight()) - self.height
        ))

    def draw(self):
        gpu.state.blend_set("ALPHA")
        self._setup_draw()
        if self.texture is None:
            super().draw()
            return
        if self._ubo is None:
            self._ubo = gpu.types.GPUUniformBuf(self._ubo_data)
        else:
            self._ubo.update(self._ubo_data)
        self._shader.uniform_block("ubo", self._ubo)
        self._shader.uniform_sampler("image", self.texture)
        self._shader.bind()
        self._batch.draw(self._shader)

    def _draw_custom_cursor(self):
        if self.show:
            self.pos = MOUSE.position
            self._build_shader()
            self.draw()

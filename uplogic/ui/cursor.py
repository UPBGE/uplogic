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
    scene = bge.logic.getCurrentScene()
    to_remove = []
    for f in scene.post_draw:
        if f.__name__ == '_draw_custom_cursor':
            to_remove.append(f)
    for f in to_remove:
        scene.post_draw.remove(f)


def set_custom_cursor(texture=None, size=(30,30), offset=(0, 0), rows=1, cols=1, idx=0):
    return Cursor(texture=texture, size=size, offset=offset, rows=rows, cols=cols, idx=idx)


class Cursor(Sprite):

    def __init__(self, texture=None, size=(30,30), offset=(0, 0), rows=1, cols=1, idx=0):
        self.offset = offset
        self._idx = idx
        super().__init__(MOUSE.position, size, cols=cols, rows=rows, idx=idx)
        remove_custom_cursor()
        self._texture = None
        self._shader = None
        self.texture = texture
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
        self._shader.uniform_sampler("image", self.texture)
        self._shader.bind()
        self._batch.draw(self._shader)

    def _draw_custom_cursor(self):
        if self._show_effective:
            self.pos = MOUSE.position
            self._build_shader()
            self.draw()

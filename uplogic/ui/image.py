from .widget import Widget
import gpu
import bge, bpy
from math import ceil
from uplogic.utils.math import rotate2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


class Image(Widget):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, halign='left', valign='bottom', angle=0):
        super().__init__(pos, size, relative=relative, halign=halign, valign=valign, angle=angle)
        self.texture = texture

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, val):
        texture = bpy.data.images.get(val)
        if texture:
            self._texture = gpu.texture.from_image(texture)

    def _build_shader(self):
        pos = self._draw_pos
        size = self._draw_size
        x0 = Vector((pos[0], pos[1]))
        x1 = Vector((pos[0] + size[0], pos[1]))
        y1 = Vector((pos[0] + size[0], pos[1] + size[1]))
        y0 = Vector((pos[0], pos[1] + size[1]))
        pivot = self._get_pivot(x0, x1, y0, y1)

        if self._draw_angle and self._vertices is not None:
            x0 = rotate2d(x0, pivot, self._draw_angle)
            x1 = rotate2d(x1, pivot, self._draw_angle)
            y0 = rotate2d(y0, pivot, self._draw_angle)
            y1 = rotate2d(y1, pivot, self._draw_angle)
        vertices = self._vertices = (
            x0, x1, y1, y0
        )
        self._shader = gpu.shader.from_builtin('IMAGE_COLOR')
        self._batch = batch_for_shader(
            self._shader, 'TRI_FAN',
            {
                "pos": vertices,
                "texCoord": ((0.0001, 0.0001), (.9999, .0001), (.9999, .9999), (.0001, .9999)),
            },
        )
    
    def draw(self):
        super()._setup_draw()
        self._shader.bind()
        self._shader.uniform_sampler("image", self.texture)
        self._batch.draw(self._shader)
        super().draw()


class Sprite(Image):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, idx=0, rows=1, cols=1, halign='left', valign='bottom'):
        self._idx = idx
        self.rows = rows
        self.cols = cols
        super().__init__(pos, size, relative, texture, halign=halign, valign=valign)

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, val):
        self._idx = val
        self._build_shader()

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, val):
        if val < 1:
            return
        self._rows = val
        self._row_height = 1 / val

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, val):
        if val < 1:
            return
        self._cols = val
        self._col_width = 1 / val

    def _build_shader(self):
        pos = self._draw_pos
        size = self._draw_size
        x0 = Vector((pos[0], pos[1]))
        x1 = Vector((pos[0] + size[0], pos[1]))
        y1 = Vector((pos[0] + size[0], pos[1] + size[1]))
        y0 = Vector((pos[0], pos[1] + size[1]))
        pivot = self._get_pivot(x0, x1, y0, y1)

        if self._draw_angle and self._vertices is not None:
            x0 = rotate2d(x0, pivot, self._draw_angle)
            x1 = rotate2d(x1, pivot, self._draw_angle)
            y0 = rotate2d(y0, pivot, self._draw_angle)
            y1 = rotate2d(y1, pivot, self._draw_angle)

        vertices = self._vertices = (
            x0,
            x1,
            y1,
            y0
        )
        self._shader = gpu.shader.from_builtin('IMAGE_COLOR')
        idx = self.idx
        col = idx % self.cols
        col_end = col + 1
        row = ceil((idx + 1) / self.cols) - 1
        row_end = row + 1
        texcoord = (
            (col * self._col_width, 1 - row_end * self._row_height),
            (col_end * self._col_width, 1 - row_end * self._row_height),
            (col_end * self._col_width, 1 - row * self._row_height),
            (col * self._col_width, 1 - row * self._row_height)
        )
        self._batch = batch_for_shader(
            self._shader, 'TRI_FAN',
            {
                "pos": vertices,
                "texCoord": texcoord
            },
        )
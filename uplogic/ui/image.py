from .widget import Widget
import gpu
import bge, bpy
from math import ceil
from gpu_extras.batch import batch_for_shader


class Image(Widget):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, halign='left', valign='bottom'):
        super().__init__(pos, size, relative=relative, halign=halign, valign=valign)
        self.texture = texture

    @property
    def texture(self):
        return self._texture
        
    @texture.setter
    def texture(self, val):
        texture = bpy.data.images.get(val)
        if texture:
            self._texture = gpu.texture.from_image(texture)

    def build_shader(self):
        pos = self._draw_pos
        size = self._draw_size
        vertices = self._vertices = (
            (pos[0], pos[1]),
            (pos[0] + size[0], pos[1]),
            (pos[0] + size[0], pos[1] + size[1]),
            (pos[0], pos[1] + size[1])
        )
        self._shader = gpu.shader.from_builtin('2D_IMAGE')
        self._batch = batch_for_shader(
            self._shader, 'TRI_FAN',
            {
                "pos": vertices,
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )
    
    def draw(self):
        super()._setup_draw()
        self._shader.bind()
        self._shader.uniform_sampler("image", self.texture)
        self._batch.draw(self._shader)
        super().draw()


class Icon(Image):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, icon=0, rows=1, cols=1, halign='left', valign='bottom'):
        super().__init__(pos, size, relative, texture, halign=halign, valign=valign)
        self.icon = icon
        self.rows = rows
        self.cols = cols

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

    def build_shader(self):
        pos = self._draw_pos
        size = self._draw_size
        vertices = self._vertices = (
            (pos[0], pos[1]),
            (pos[0] + size[0], pos[1]),
            (pos[0] + size[0], pos[1] + size[1]),
            (pos[0], pos[1] + size[1])
        )
        self._shader = gpu.shader.from_builtin('2D_IMAGE')
        icon = self.icon
        col = icon % self.cols
        col_end = col + 1
        row = ceil((icon + 1) / self.cols) - 1
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
from .widget import Widget
import gpu
import bge, bpy
from math import ceil
from uplogic.utils.math import rotate2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from os.path import isfile


class Image(Widget):

    vertex_shader = """
    in vec2 texCoord;
    in vec2 pos;
    out vec2 uv;

    uniform mat4 ModelViewProjectionMatrix;

    void main() {
        uv = texCoord;
        gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0, 1.0);
    }
    """

    fragment_shader = """
    in vec2 uv;
    out vec4 fragColor;

    uniform sampler2D image;
    uniform float alpha = 1.0;

    void main() {
        vec4 color = mix(vec4(0.0), texture(image, uv), alpha);
        fragColor = pow(color, vec4(.5));
    }
    """

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, halign='left', valign='bottom', use_aspect_ratio: bool = True, angle=0):
        self._texture = None
        self._image = None
        self.use_aspect_ratio = use_aspect_ratio
        self._opacity = 1
        super().__init__(pos, size, relative=relative, halign=halign, valign=valign, angle=angle)
        if texture not in bpy.data.images and isfile(texture):
            bpy.data.images.load(texture)
        self.texture = texture
        self.start()

    @property
    def texture(self):
        return self._texture

    @property
    def aspect_ratio(self):
        if self._image is None:
            return 1
        return self._image.size[1] / self._image.size[0]

    @property
    def _draw_size(self):
        size = self.size.copy()
        use_aspect_ratio = self.use_aspect_ratio
        if self.parent is None:
            return size
        if use_aspect_ratio and self._image:
            size[1] = size[0] * self.aspect_ratio
        if self.relative.get('size'):
            pdsize = self.parent._draw_size
            size = [
                size[0] * pdsize[0],
                size[1] * (pdsize[0] if use_aspect_ratio else pdsize[1])
            ]
        return size

    @texture.setter
    def texture(self, val):
        if val is None:
            return
        texture = bpy.data.images.get(val, None)
        if not texture:
            texture = bpy.data.images.load(val)
        self._image = texture
        self.size = self.size
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
            x1, x0, y1, y0
        )

        self._shader = gpu.types.GPUShader(self.vertex_shader, self.fragment_shader)
        self._batch = batch_for_shader(
            self._shader, 'TRI_STRIP',
            {
                "pos": vertices,
                "texCoord": (
                    (.9999, .0001),
                    (0.0001, 0.0001),
                    (.9999, .9999),
                    (.0001, .9999)
                ),
            },
        )
    
    def draw(self):
        gpu.state.blend_set("ALPHA")
        super()._setup_draw()
        if self.texture is None:
            super().draw()
            return
        self._shader.bind()
        self._shader.uniform_float("alpha", self.opacity)
        self._shader.uniform_sampler("image", self.texture)
        self._batch.draw(self._shader)
        super().draw()


class Sprite(Image):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, idx=0, rows=1, cols=1, halign='left', valign='bottom', use_aspect_ratio=True):
        self._idx = idx
        self.rows = rows
        self.cols = cols
        super().__init__(pos, size, relative, texture, halign=halign, valign=valign, use_aspect_ratio=use_aspect_ratio)

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, val):
        self._idx = val
        self._build_shader()

    @property
    def aspect_ratio(self):
        if self._image is None:
            return 1
        return (self._image.size[1] / self.rows) / (self._image.size[0] / self.cols)

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
            x1,
            x0,
            y1,
            y0
        )

        tex_vert_shader = """
        in vec2 texCoord;
        in vec2 pos;
        out vec2 uv;

        uniform mat4 ModelViewProjectionMatrix;

        void main() {
            uv = texCoord;
            gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0, 1.0);
        }
        """

        tex_frag_shader = """
        in vec2 uv;
        out vec4 fragColor;

        uniform sampler2D image;
        uniform float alpha = 1.0;

        void main() {
            vec4 color = mix(vec4(0.0), texture(image, uv), alpha);
            fragColor = pow(color, vec4(.5));
        }
        """
        self._shader = gpu.types.GPUShader(tex_vert_shader, tex_frag_shader)
        self._shader.uniform_float("alpha", self.opacity)

        idx = self.idx
        col = idx % self.cols
        col_end = col + 1
        row = ceil((idx + 1) / self.cols) - 1
        row_end = row + 1
        texcoord = (
            (col_end * self._col_width, 1 - row_end * self._row_height),
            (col * self._col_width, 1 - row_end * self._row_height),
            (col_end * self._col_width, 1 - row * self._row_height),
            (col * self._col_width, 1 - row * self._row_height)
        )
        self._batch = batch_for_shader(
            self._shader, 'TRI_STRIP',
            {
                "pos": vertices,
                "texCoord": texcoord
            },
        )
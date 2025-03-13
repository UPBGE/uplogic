from .widget import Widget
import gpu
import bpy
from bge import logic
from math import ceil
from uplogic.utils import clamp
from .widget import rotate2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from os.path import isfile
from uplogic.utils.handlers import ImageHandler


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
    def __init__(
        self,
        pos=[0, 0],
        size=(100, 100),
        relative={},
        texture=None,
        halign='left',
        valign='bottom',
        use_aspect_ratio: bool = True,
        angle=0,
        show=True
    ):
        self._texture = None
        self._image = None
        self.use_aspect_ratio = use_aspect_ratio
        self._opacity = 1
        super().__init__(pos, size, relative=relative, halign=halign, valign=valign, angle=angle, show=show)
        self._load_image(texture)

    def _load_image(self, texture):
        self.image_handler = ImageHandler(texture)
        self.start()

    @property
    def filepath(self):
        return self.image_handler.filepath

    @property
    def texture(self):
        return self.image_handler._texture

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
        self.image_handler.texture = val
        self.size = self.size

    def free(self):
        self.image_handler.free()

    @property
    def frame(self):
        return self.image_handler.frame

    @frame.setter
    def frame(self, val):
        self.image_handler.frame = val

    @property
    def max_frame(self):
        return self.image_handler.max_frame

    @property
    def pivot(self):
        """Rotation point for this widget."""
        if self.parent is None:
            return (0, 0)
        v = self._vertices
        x0 = Vector(v[1])
        x1 = Vector(v[0])
        y1 = Vector(v[2])
        y0 = Vector(v[3])
        return Vector(self._get_pivot(x0, x1, y0, y1))

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

        if bpy.app.version[0] < 4:
            self._shader = gpu.shader.from_builtin('2D_IMAGE')
        else:
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
        if bpy.app.version[0] >= 4:
            self._shader.uniform_float("alpha", self.opacity)
        self._shader.uniform_sampler("image", self.texture)
        self._batch.draw(self._shader)
        super().draw()


class Sprite(Image):

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

    def __init__(
        self,
        pos=[0, 0],
        size=(100, 100),
        relative={},
        texture=None,
        idx=0,
        rows=1,
        cols=1,
        halign='left',
        valign='bottom',
        use_aspect_ratio=True,
        show=True
    ):
        self._idx = idx
        self.rows = rows
        self.cols = cols
        super().__init__(pos, size, relative, texture, halign=halign, valign=valign, use_aspect_ratio=use_aspect_ratio, show=show)

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

        if bpy.app.version[0] < 4:
            self._shader = gpu.shader.from_builtin('2D_IMAGE')
        else:
            self._shader = gpu.types.GPUShader(self.tex_vert_shader, self.tex_frag_shader)
        if bpy.app.version[0] >= 4:
            self._shader.uniform_float("alpha", self.opacity)
        else:
            self._shader.uniform_sampler("image", self.texture)

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


class Video(Image):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, halign='left', valign='bottom', use_aspect_ratio = True, fps=60, min_frame=0, max_frame=None, load_audio=True, angle=0, show=True):
        self._load_audio = load_audio
        super().__init__(pos, size, relative, texture, halign, valign, use_aspect_ratio, angle, show)
        self.image_handler.fps = fps
        self.image_handler._min_frame = min_frame
        if max_frame is not None:
            self.image_handler._max_frame = max_frame

    def _load_image(self, texture):
        self.image_handler = ImageHandler(texture, load_audio=self._load_audio)

    @property
    def fps(self):
        return self.image_handler.fps

    @fps.setter
    def fps(self, val):
        self.image_handler.fps = val

    @property
    def playback_position(self):
        return self.image_handler.playback_position

    @property
    def is_playing(self):
        return self.image_handler.is_playing

    @is_playing.setter
    def is_playing(self, val):
        self.image_handler.is_playing = val

    def play(self):
        self.image_handler.play()

    def seek(self, position):
        self.image_handler.seek(position)

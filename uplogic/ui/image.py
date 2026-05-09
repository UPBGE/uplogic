from .widget import Widget
import gpu
import bpy
from math import ceil
from .widget import rotate2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from uplogic.handlers.imagehandler import ImageHandler
from uplogic.utils import clamp



class _UV_Point(list):

    @property
    def lower(self):
        return self[0]

    @lower.setter
    def lower(self, val):
        self[0] = val

    @property
    def upper(self):
        return self[1]

    @upper.setter
    def upper(self, val):
        self[1] = val


class _UV(list):

    @property
    def owner(self) -> Widget:
        return self[2]

    @property
    def x(self) -> _UV_Point:
        return self[0]

    @x.setter
    def x(self, val):
        self[0] = _UV_Point(val)
        self.owner._build_shader()

    @property
    def x_min(self) -> _UV_Point:
        return self.x.lower

    @x_min.setter
    def x_min(self, val):
        self.x.lower = val
        self.owner._build_shader()

    @property
    def x_max(self) -> _UV_Point:
        return self.x.upper

    @x_max.setter
    def x_max(self, val):
        self.x.upper = val
        self.owner._build_shader()

    @property
    def y(self) -> _UV_Point:
        return self[1]

    @y.setter
    def y(self, val):
        self[1] = _UV_Point(val)
        self.owner._build_shader()

    @property
    def y_min(self) -> _UV_Point:
        return self.y.lower

    @y_min.setter
    def y_min(self, val):
        self.y.lower = val
        self.owner._build_shader()

    @property
    def y_max(self) -> _UV_Point:
        return self.y.upper

    @y_max.setter
    def y_max(self, val):
        self.y.upper = val
        self.owner._build_shader()


class Image(Widget):

    vertex_in = [
        ('VEC2', 'texCoord'),
        ('VEC2', 'position')
    ]

    interfaces = [
        ('VEC2', "pos"),
        ('VEC2', 'uv')
    ]

    constants = [
        ('FLOAT', 'alpha'),
        ('FLOAT', 'saturation')
    ]

    samplers = [
        ('FLOAT_2D', 'image')
    ]

    vertex_shader = """

    void main()
    {
        uv = texCoord;
        pos = position;
        gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0, 1.0);
    }
    """

    fragment_shader = """

    void main()
    {
        vec4 color = texture(image, uv);
        
        float power = clamp(saturation, 0.0, 1.0);

        float grey = (color.r + color.g + color.b) * .33;
        color = vec4(
            color.r * power + grey * (1.0 - power),
            color.g * power + grey * (1.0 - power),
            color.b * power + grey * (1.0 - power),
            color.a * alpha
        );
        FragColor = pow(color, vec4(0.5));
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
        self.use_aspect_ratio = use_aspect_ratio
        self._uv: _UV[_UV_Point] = _UV((_UV_Point((0.01, .99)), _UV_Point((0.01, .99)), self))
        self._opacity = 1
        self._saturation = 1
        self._load_image(texture)
        super().__init__(pos, size, relative=relative, halign=halign, valign=valign, angle=angle, show=show)

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, val):
        if val == self._saturation:
            return
        self._saturation = clamp(val, 0, 1)
        self._rebuild = True

    @property
    def uv(self):
        return self._uv

    @uv.setter
    def uv(self, val):
        self._uv = val
        self._build_shader()

    @property
    def image(self):
        return self.image_handler.image

    def _load_image(self, texture):
        self.image_handler = ImageHandler(texture)
        self.start()

    @property
    def size_pixel(self):
        if self._vertices is None:
            return [0, 0]
        bottom_left = self._vertices[1]
        top_right = self._vertices[2]
        return [top_right[0] - bottom_left[0], top_right[1] - bottom_left[1]]

    @property
    def filepath(self):
        return self.image_handler.filepath

    @property
    def texture(self):
        return self.image_handler._texture

    @property
    def aspect_ratio(self):
        if self.image is None:
            return 1
        return self.image.size[1] / self.image.size[0]

    @property
    def _draw_size(self):
        size = self.size.copy()
        use_aspect_ratio = self.use_aspect_ratio
        if self.parent is None:
            return size
        if use_aspect_ratio and self.image:
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

    def _get_vertices(self, pos, size):
        return super()._get_vertices(pos, size)

    def _get_uvs(self):
        return [self.uv.x.copy(), self.uv.y.copy()]

    def _build_shader(self, force=True):
        pos = self._draw_pos
        size = self._draw_size

        self._shader = self._get_shader()
        self._vertices = self._get_vertices(pos, size)
        uvs = self._get_uvs()
        self._set_uniforms()

        self._batch = batch_for_shader(
            self._shader, 'TRI_STRIP',
            {
                "position": self._vertices,
                "texCoord": (
                    (uvs[0][1], uvs[1][0]),
                    (uvs[0][0], uvs[1][0]),
                    (uvs[0][1], uvs[1][1]),
                    (uvs[0][0], uvs[1][1])
                ),
            },
        )
    
    def _set_uniforms(self):
        self._shader.uniform_float("alpha", self.opacity)
        self._shader.uniform_float("saturation", self.saturation)

    def draw(self):
        gpu.state.blend_set("ALPHA")
        self._setup_draw()
        if self.texture is None:
            super().draw()
            return
        self._shader.uniform_sampler("image", self.texture)
        self._shader.bind()
        self._batch.draw(self._shader)
        super().draw()


class Sprite(Image):

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
        # self._idx = idx
        self.rows = rows
        self.cols = cols
        super().__init__(pos, size, relative, texture, halign=halign, valign=valign, use_aspect_ratio=use_aspect_ratio, show=show)
        self.idx = idx

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, val):
        self._idx = val
        self._get_uv()

    def _get_uv(self):
        ...
        idx = self.idx
        col = idx % self.cols
        col_end = col + 1
        row = ceil((idx + 1) / self.cols) - 1
        row_end = row + 1
        self.uv.y_max = 1 - row * self._row_height
        self.uv.y_min = 1 - row_end * self._row_height
        self.uv.x_max = col_end * self._col_width
        self.uv.x_min = col * self._col_width

    @property
    def aspect_ratio(self):
        if self.image is None:
            return 1
        return (self.image.size[1] / self.rows) / (self.image.size[0] / self.cols)

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, val):
        if val < 1:
            return
        self._rows = int(val)
        self._row_height = 1 / int(val)

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, val):
        if val < 1:
            return
        self._cols = int(val)
        self._col_width = 1 / int(val)

class Video(Image):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None, halign='left', valign='bottom', use_aspect_ratio = True, fps=60, min_frame=0, max_frame=None, load_audio=True, play_mode='play', angle=0, show=True):
        self._load_audio = load_audio
        # self.play_mode = play_mode
        super().__init__(pos, size, relative, texture, halign, valign, use_aspect_ratio, angle, show)
        self.image_handler.fps = fps
        self.image_handler._min_frame = min_frame
        if max_frame is not None:
            self.image_handler._max_frame = max_frame

    def _load_image(self, texture):
        self.image_handler = ImageHandler(texture, load_audio=self._load_audio)

    @property
    def play_mode(self):
        return self.image_handler.play_mode

    @play_mode.setter
    def play_mode(self, val):
        self.image_handler.play_mode = val

    @property
    def texture(self):
        return self.image_handler.texture

    @texture.setter
    def texture(self, val):
        self.image_handler.texture = val

    @property
    def fps(self):
        return self.image_handler.fps

    @fps.setter
    def fps(self, val):
        self.image_handler.fps = val

    @property
    def playback_position(self):
        return self.image_handler.playback_position

    @playback_position.setter
    def playback_position(self, val):
        self.image_handler.playback_position = val

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

    def stop(self):
        self.image_handler.stop()

    def remove(self):
        self.free()
        return super().remove()

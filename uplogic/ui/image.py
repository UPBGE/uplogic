from .widget import Widget
import gpu
import bpy
from math import ceil
from .widget import rotate2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from uplogic.handlers.imagehandler import ImageHandler
from uplogic.utils import clamp



'''Image, sprite-sheet, and video widgets for uplogic UI.'''


class _UV_Point(list):
    '''Internal helper: a two-element list with named :attr:`lower` / :attr:`upper` accessors.'''

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
    '''Internal UV coordinate container holding ``[x_range, y_range, owner_widget]``.

    Setting ``x``, ``y``, or their ``min``/``max`` sub-properties triggers a
    shader rebuild on the owning :class:`Image` widget.
    '''

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
    '''Widget that displays a texture image.

    Uses a custom fragment shader that applies :attr:`opacity` (alpha) and
    :attr:`saturation` (greyscale mix).  When :attr:`use_aspect_ratio` is
    ``True`` the height is derived from the image's pixel aspect ratio so
    the image is never stretched.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param relative: Relative positioning/sizing flags.
    :param texture: File path or ``bpy.types.Image`` name to display.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param use_aspect_ratio: Preserve the image's pixel aspect ratio.
        Defaults to ``True``.
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

    vertex_in = [
        ('VEC2', 'texCoord'),
        ('VEC2', 'position')
    ]

    interfaces = [
        ('VEC2', "pos"),
        ('VEC2', 'uv')
    ]

    constants = []

    ubo_constants = [
        ('VEC4', 'image_params'),   # x=alpha  y=saturation  z=brightness  w=blur
        ('VEC4', 'multiply_color'),
        ('VEC4', 'size_params'),    # xy=tex_size  zw=shadow_offset_uv (pre-converted from screen pixels)
        ('VEC4', 'shadow_color'),
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
        float alpha         = ubo.image_params.x;
        float saturation    = ubo.image_params.y;
        float brightness    = ubo.image_params.z;
        float blur          = ubo.image_params.w;
        vec2  tex_size      = ubo.size_params.xy;
        vec2  shadow_offset = ubo.size_params.zw;

        vec2 texel = 1.0 / tex_size;
        vec2 half_texel = 0.5 * texel;

        vec4 color;
        if (blur < 0.5) {
            color = texture(image, clamp(uv, half_texel, 1.0 - half_texel));
        } else {
            int r = int(blur + 0.5);
            float sigma = blur * 0.5;
            float inv_sigma2 = 0.5 / (sigma * sigma);
            float total = 0.0;
            color = vec4(0.0);
            for (int x = -r; x <= r; x++) {
                for (int y = -r; y <= r; y++) {
                    float d2 = float(x * x + y * y);
                    if (d2 > float(r * r)) continue;
                    float w = exp(-d2 * inv_sigma2);
                    vec2 target_uv = uv + vec2(float(x), float(y)) * texel;
                    color += texture(image, clamp(target_uv, half_texel, 1.0 - half_texel)) * w;
                    total += w;
                }
            }
            color /= total;
        }

        float power = clamp(saturation, 0.0, 1.0);

        float grey = (color.r + color.g + color.b) * .33;
        color = vec4(
            color.r * power + grey * (1.0 - power),
            color.g * power + grey * (1.0 - power),
            color.b * power + grey * (1.0 - power),
            color.a * alpha
        );
        vec4 main_out = vec4(pow(color.rgb, vec3(0.5)), color.a) * ubo.multiply_color * brightness;

        vec2 shadow_uv = uv - shadow_offset;
        float s_alpha = 0.0;
        if (shadow_uv.x >= 0.0 && shadow_uv.x <= 1.0 && shadow_uv.y >= 0.0 && shadow_uv.y <= 1.0) {
            s_alpha = texture(image, clamp(shadow_uv, half_texel, 1.0 - half_texel)).a * ubo.shadow_color.a * alpha;
        }
        vec4 shadow_px = vec4(ubo.shadow_color.rgb, s_alpha);
        FragColor = main_out + shadow_px * (1.0 - main_out.a);
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
        shadow_offset=(0, 0),
        shadow_color=(0., 0., 0., 0.),
        show=True
    ):
        self._texture = None
        self.use_aspect_ratio = use_aspect_ratio
        self._uv: _UV[_UV_Point] = _UV((_UV_Point((0.0, 1)), _UV_Point((0.0, 1)), self))
        self._opacity = 1
        self._saturation = 1
        self._multiply_color = Vector((1, 1, 1, 1))
        self._brightness = 1
        self._blur_radius = 0
        self._shadow_offset = Vector(shadow_offset)
        self._shadow_color = Vector(shadow_color)
        self._ubo = None
        self._ubo_data = bytes(64)
        self._load_image(texture)
        super().__init__(pos, size, relative=relative, halign=halign, valign=valign, angle=angle, show=show)
            # import bge
            # bge.logic.endGame()

    @property
    def saturation(self):
        '''Colour saturation in ``[0.0, 1.0]``: ``0`` = greyscale, ``1`` = full colour.'''
        return self._saturation

    @saturation.setter
    def saturation(self, val):
        if val == self._saturation:
            return
        self._saturation = clamp(val, 0, 1)
        self._rebuild = True

    @property
    def multiply_color(self) -> Vector:
        '''Color multiplier for the GPU texture with 4 components (r, g, b, a).'''
        return self._multiply_color

    @multiply_color.setter
    def multiply_color(self, val):
        if val == self._multiply_color:
            return
        self._multiply_color = Vector(val)
        self._rebuild = True

    @property
    def brightness(self) -> Vector:
        '''Brightness  in ``[0.0, 1.0]``: ``0`` = black, ``1`` = full brightness.'''
        return self._brightness

    @brightness.setter
    def brightness(self, val):
        if val == self._brightness:
            return
        self._brightness = val
        self._rebuild = True

    @property
    def blur_radius(self):
        '''Gaussian blur radius in pixels. ``0`` = no blur.'''
        return self._blur_radius

    @blur_radius.setter
    def blur_radius(self, val):
        val = max(0, val)
        if val == self._blur_radius:
            return
        self._blur_radius = val
        self._rebuild = True

    @property
    def shadow_offset(self) -> Vector:
        '''Drop shadow offset in screen pixels ``[x, y]``. Set :attr:`shadow_color` alpha > 0 to enable.'''
        return self._shadow_offset

    @shadow_offset.setter
    def shadow_offset(self, val):
        val = Vector(val)
        if val == self._shadow_offset:
            return
        self._shadow_offset = val
        self._rebuild = True

    @property
    def shadow_color(self) -> Vector:
        '''RGBA colour of the drop shadow. Set alpha > 0 to make the shadow visible.'''
        return self._shadow_color

    @shadow_color.setter
    def shadow_color(self, val):
        val = Vector(val)
        if val == self._shadow_color:
            return
        self._shadow_color = val
        self._rebuild = True

    @property
    def uv(self):
        '''Active :class:`_UV` mapping.  Setting this rebuilds the shader immediately.'''
        return self._uv

    @uv.setter
    def uv(self, val):
        self._uv = val
        self._build_shader()

    @property
    def image(self):
        '''Underlying ``bpy.types.Image`` via the ``ImageHandler``, or ``None``.'''
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
        '''File path of the loaded image.'''
        return self.image_handler.filepath

    @property
    def texture(self):
        '''GPU texture object used by the shader.  Setting this reloads and re-sizes the image.'''
        return self.image_handler._texture

    @property
    def aspect_ratio(self):
        '''``image.height / image.width``, or ``1.0`` when no image is loaded.'''
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
        '''Release the GPU texture via the ``ImageHandler``.'''
        self.image_handler.free()

    @property
    def frame(self):
        '''Current animation frame index (delegates to ``ImageHandler``).'''
        return self.image_handler.frame

    @frame.setter
    def frame(self, val):
        self.image_handler.frame = val

    @property
    def max_frame(self):
        '''Maximum animation frame index (delegates to ``ImageHandler``).'''
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
        import struct
        img = self.image
        tex_size = img.size[:2] if img else (1.0, 1.0)
        uv = self.uv
        draw_size = self._draw_size
        w = max(draw_size[0], 1)
        h = max(draw_size[1], 1)
        shadow_uv = (
            self._shadow_offset[0] * (uv.x[1] - uv.x[0]) / w,
            self._shadow_offset[1] * (uv.y[1] - uv.y[0]) / h,
        )
        self._ubo_data = struct.pack(
            '16f',
            self.opacity, self.saturation, self.brightness, self._blur_radius,
            *self.multiply_color,
            *tex_size, *shadow_uv,
            *self._shadow_color,
        )

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
        super().draw()


class Sprite(Image):
    '''Widget that displays a single frame from a sprite sheet.

    Subdivides the texture UV space into a *rows* × *cols* grid.  Setting
    :attr:`idx` selects which cell to display (left-to-right, top-to-bottom).

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param relative: Relative positioning/sizing flags.
    :param texture: Sprite-sheet image path.
    :param idx: Zero-based cell index.
    :param rows: Number of rows in the sprite sheet.
    :param cols: Number of columns in the sprite sheet.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param use_aspect_ratio: Preserve per-cell aspect ratio.
    :param show: Initial visibility.
    '''

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
        '''Active sprite sheet cell index (zero-based, left-to-right/top-to-bottom).
        Setting recalculates the UV coordinates.
        '''
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
        '''Number of rows in the sprite sheet.  Setting updates the per-row UV step.'''
        return self._rows

    @rows.setter
    def rows(self, val):
        if val < 1:
            return
        self._rows = int(val)
        self._row_height = 1 / int(val)

    @property
    def cols(self):
        '''Number of columns in the sprite sheet.  Setting updates the per-column UV step.'''
        return self._cols

    @cols.setter
    def cols(self, val):
        if val < 1:
            return
        self._cols = int(val)
        self._col_width = 1 / int(val)

class Video(Image):
    '''Widget that plays back a video file as an animated image.

    Extends :class:`Image` with playback controls.  The ``ImageHandler``
    drives frame advance and optional audio loading.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param relative: Relative positioning/sizing flags.
    :param texture: Video file path.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param use_aspect_ratio: Preserve aspect ratio.
    :param fps: Playback frame rate.
    :param min_frame: First frame to play.
    :param max_frame: Last frame to play; ``None`` uses the full clip length.
    :param load_audio: Whether to load the audio track alongside the video.
    :param play_mode: Playback mode string passed to ``ImageHandler``.
    :param angle: Rotation in degrees.
    :param show: Initial visibility.
    '''

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
        '''Playback mode string (e.g. ``'play'``, ``'loop'``).'''
        return self.image_handler.play_mode

    @play_mode.setter
    def play_mode(self, val):
        self.image_handler.play_mode = val

    @property
    def texture(self):
        '''GPU texture object; delegates to ``ImageHandler``.'''
        return self.image_handler.texture

    @texture.setter
    def texture(self, val):
        self.image_handler.texture = val

    @property
    def fps(self):
        '''Playback frame rate.'''
        return self.image_handler.fps

    @fps.setter
    def fps(self, val):
        self.image_handler.fps = val

    @property
    def playback_position(self):
        '''Current playback position in the video.'''
        return self.image_handler.playback_position

    @playback_position.setter
    def playback_position(self, val):
        self.image_handler.playback_position = val

    @property
    def is_playing(self):
        '''``True`` while the video is actively playing.'''
        return self.image_handler.is_playing

    @is_playing.setter
    def is_playing(self, val):
        self.image_handler.is_playing = val

    def play(self):
        '''Start video playback.'''
        self.image_handler.play()

    def seek(self, position):
        '''Jump to *position* in the video.

        :param position: Target playback position.
        '''
        self.image_handler.seek(position)

    def stop(self):
        '''Stop video playback.'''
        self.image_handler.stop()

    def remove(self):
        '''Free the GPU texture and remove this widget from its parent.'''
        self.free()
        return super().remove()

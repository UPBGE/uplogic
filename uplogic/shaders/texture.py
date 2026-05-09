from .shader import Filter2D
import bpy, bge
from mathutils import Vector
from ..console import error


class Texture(Filter2D):
    '''Overlays a ``bpy.types.Image`` on top of the rendered frame.

    The image is drawn within the screen-space rectangle defined by ``pos``
    (bottom-left UV corner) and ``size`` (UV extent). Pixels outside that
    rectangle are passed through at full opacity. The image is loaded and
    GL-prepared (``gl_load()``) on construction.

    Setting ``free_textures = True`` (the default) causes the previous
    image's GL buffer to be freed automatically whenever the :attr:`texture`
    property is assigned a new value.
    '''

    glsl = """
uniform sampler2D bgl_RenderedTexture;
uniform sampler2D tex;
uniform float opacity;
uniform vec2 pos;
uniform vec2 size;

// in vec4 bgl_TexCoord;

// out vec4 fragColor;


float map_range(float value, float in_min, float in_max, float out_min, float out_max){
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}


void main()
{

    vec2 texcoord = bgl_TexCoord.xy;
    float opa = opacity;

    if (texcoord.x < pos.x || texcoord.x > pos.x + size.x || texcoord.y < pos.y || texcoord.y > pos.y + size.y){
        opa = 0;
    }

    vec2 texMap = vec2(
        map_range(texcoord.x, pos.x, pos.x + size.x, 0, 1),
        map_range(texcoord.y, pos.y, pos.y + size.y, 0, 1)
    );
    fragColor = mix(
        texture(bgl_RenderedTexture, texcoord),
        texture(tex, texMap),
        opa
    );
}
"""

    def __init__(self, texture: bpy.types.Image = None, opacity: float = 1.0, pos=Vector((0, 0)), size=Vector((1, 1)), idx: int = None) -> None:
        '''Initialise the Texture overlay filter.

        If ``texture`` is a path string it is loaded with
        ``bpy.data.images.load``; if it is already a ``bpy.types.Image`` it
        is used directly. ``gl_load()`` is called to upload pixel data to the
        GPU.

        :param texture: Path string or ``bpy.types.Image`` to overlay on the
            rendered frame.
        :param opacity: Blend weight. ``0`` is fully transparent;
            ``1`` shows the texture at full opacity.
        :param pos: Bottom-left UV coordinate of the overlay rectangle as a
            two-component ``Vector``.
        :param size: UV extent (width, height) of the overlay rectangle as a
            two-component ``Vector``.
        :param idx: Filter pass index. ``None`` assigns the next available
            index automatically.
        '''
        texture_ = bpy.data.images.get(str(texture), texture)
        if not isinstance(texture_, bpy.types.Image):
            texture_ = bpy.data.images.load(texture)
        texture_.gl_load()
        self.free_textures = True
        self.uniforms = {'tex': texture_, 'opacity': float(opacity), 'pos': Vector(pos), 'size': Vector(size)}
        super().__init__(self.glsl, idx, {'tex': self.uniforms, 'opacity': self.uniforms, 'pos': self.uniforms, 'size': self.uniforms})

    @property
    def texture(self) -> bpy.types.Image:
        '''The current overlay image (``bpy.types.Image``).

        When set, the new value must be a ``bpy.types.Image``. If
        ``free_textures`` is ``True`` the previous image's GL buffer is freed
        via :meth:`free_texture` before the new image is assigned.
        Raises ``TypeError`` if a non-image value is provided.
        '''
        return self.uniforms['tex']

    @texture.setter
    def texture(self, val):
        if self.free_textures:
            self.free_texture()
        if not isinstance(val, bpy.types.Image):
            raise TypeError
        if not val.has_data:
            val.gl_load()
        self.uniforms['tex'] = val

    def free_texture(self):
        '''Free the GL buffer and CPU pixel data of the current texture image.

        Calls ``gl_free()`` and ``buffers_free()`` on the image stored in
        :attr:`uniforms` ``['tex']`` to release GPU and CPU memory.
        '''
        self.uniforms['tex'].gl_free()
        self.uniforms['tex'].buffers_free()

    @property
    def opacity(self):
        '''Blend weight of the overlay (``float``). ``0`` transparent, ``1`` fully opaque.'''
        return self.uniforms['opacity']

    @opacity.setter
    def opacity(self, val):
        self.uniforms['opacity'] = float(val)

    @property
    def pos(self):
        '''Bottom-left UV position of the overlay rectangle (2D ``Vector``).'''
        return self.uniforms['pos']

    @pos.setter
    def pos(self, val):
        self.uniforms['pos'] = Vector(val).to_2d()

    @property
    def size(self):
        '''UV extent (width, height) of the overlay rectangle (2D ``Vector``).'''
        return self.uniforms['size']

    @size.setter
    def size(self, val):
        self.uniforms['size'] = Vector(val).to_2d()


class Mask(Texture):
    '''Multiplies the rendered frame by a greyscale mask derived from a texture.

    Extends :class:`Texture`. Pixels within the ``pos``/``size`` rectangle are
    modulated by the greyscale value of the mask image, after optional blur and
    threshold adjustments. Pixels outside the rectangle receive a mask value of
    ``1`` (full opacity) so they pass through unchanged.

    A positive ``threshold`` value cuts darker areas of the mask by subtracting
    the threshold from each pixel before clamping, effectively raising the
    black point.
    '''

    glsl = """
uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
vec2 resolution = vec2(bgl_RenderedTextureWidth, bgl_RenderedTextureHeight);

uniform sampler2D tex;
uniform float opacity;
uniform vec2 pos;
uniform vec2 size;
uniform float threshold;
uniform int blur_samples;
uniform int blur_quality;
uniform int blur_radius;

// in vec4 bgl_TexCoord;

// out vec4 fragColor;


float map_range(float value, float in_min, float in_max, float out_min, float out_max){
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}


void main()
{
    float Pi = 6.28318530718;

    vec2 texcoord = bgl_TexCoord.xy;
    float opa = opacity;

    if (texcoord.x < pos.x || texcoord.x > pos.x + size.x || texcoord.y < pos.y || texcoord.y > pos.y + size.y){
        opa = 0;
    }

    vec2 texMap = vec2(
        map_range(texcoord.x, pos.x, pos.x + size.x, 0, 1),
        map_range(texcoord.y, pos.y, pos.y + size.y, 0, 1)
    );

    vec4 mask = mix(vec4(1.0), texture(tex, texMap), opa);

    vec2 radius = blur_radius / resolution.xy;

    for (float d = 0.0; d < Pi; d += Pi / 15)
    {
		for(float i = 1.0; i <= 1.0; i += 1.0)
        {
			mask += texture(tex, texcoord - vec2(cos(d), sin(d)) * radius * i);
        }
    }
    mask /= blur_samples;

    mask *= vec4(1 + threshold);
    mask -= vec4(threshold);

    fragColor = texture(bgl_RenderedTexture, texcoord) * clamp(mask, 0.0, 1.0);
}
"""

    def __init__(
        self,
        texture: bpy.types.Image = None,
        opacity: float = 1.0,
        pos=Vector((0, 0)),
        size=Vector((1, 1)),
        threshold=0.0,
        blur_samples=15,
        blur_radius=0.003,
        idx: int = None
    ) -> None:
        '''Initialise the Mask filter.

        The texture must already be a ``bpy.types.Image``; passing a path
        string logs an error and returns without completing initialisation.

        :param texture: ``bpy.types.Image`` used as the greyscale mask source.
        :param opacity: Blend weight controlling how strongly the mask is
            applied inside the ``pos``/``size`` region.
        :param pos: Bottom-left UV coordinate of the masked rectangle.
        :param size: UV extent (width, height) of the masked rectangle.
        :param threshold: Brightness threshold subtracted from the mask.
            Positive values cut darker areas; ``0`` applies no threshold.
        :param blur_samples: Number of samples used by the blur kernel.
        :param blur_radius: Blur kernel radius in UV units.
        :param idx: Filter pass index. ``None`` assigns the next available
            index automatically.
        '''
        texture = bpy.data.images.get(str(texture), texture)
        if not isinstance(texture, bpy.types.Image):
            error("'Texture': first argument requires an object of type 'bpy.types.Image'!")
            return
        texture.gl_load()
        self.free_textures = True
        super().__init__(texture=texture, opacity=opacity, pos=pos, size=size, idx=idx)
        self.uniforms.update({
            'blur_samples': int(blur_samples),
            'blur_radius': int(blur_radius),
            'threshold': float(threshold)
        })
        self._uniforms.update({
            'blur_samples': self.uniforms,
            'blur_radius': self.uniforms,
            'threshold': self.uniforms,
            'blur_quality': self.uniforms
        })

    @property
    def blur_radius(self):
        '''Blur kernel radius in UV units (``int`` after assignment).'''
        return self.uniforms['blur_radius']

    @blur_radius.setter
    def blur_radius(self, val):
        self.uniforms['blur_radius'] = int(val)

    @property
    def blur_samples(self):
        '''Number of samples used by the blur kernel (``int``).'''
        return self.uniforms['blur_samples']

    @blur_samples.setter
    def blur_samples(self, val):
        self.uniforms['blur_samples'] = int(val)

    @property
    def threshold(self):
        '''Brightness threshold subtracted from the mask (``float``).

        Positive values cut darker areas; ``0`` applies no threshold.
        '''
        return self.uniforms['threshold']

    @threshold.setter
    def threshold(self, val):
        self.uniforms['threshold'] = float(val)

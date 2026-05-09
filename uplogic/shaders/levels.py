from .shader import Filter2D
from mathutils import Vector


glsl = """
uniform sampler2D bgl_RenderedTexture;
// in vec4 bgl_TexCoord;
vec2 texcoord = bgl_TexCoord.xy;
uniform vec3 color;

// out vec4 fragColor;

vec4 gradient(vec4 coo)
{
    vec4 stripes = coo;
    stripes.r *= color.x;
    stripes.g *= color.y;
    stripes.b *= color.z;
    stripes.a = 1.0;
    return stripes;
}

void main (void) 
{
    vec4 value = texture(bgl_RenderedTexture, texcoord);


//     fragColor = gradient(vec4(clamp(gl_TexCoord[3].s,0.0,1.0)));
    fragColor.rgb = gradient(value).rgb;
    fragColor.a = 1.0;
}
"""

class Levels(Filter2D):
    '''Post-processing filter that applies a per-channel colour tint.

    Each RGB channel of the rendered image is multiplied by the corresponding
    component of ``color``.  At ``(1, 1, 1)`` the image is passed through
    unchanged.

    :param color: Per-channel RGB multiplier supplied as a tuple or
        ``Vector``.  Defaults to ``(1., 1., 1.)`` (no tint).
    :param idx: Render-pass index used to order filters in the pipeline.
    '''

    def __init__(self, color=(1., 1., 1.), idx: int = None) -> None:
        self.uniforms = {'color': Vector(color)}
        super().__init__(glsl, idx, {'color': self.uniforms})

    @property
    def color(self):
        '''Per-channel colour multiplier as a ``Vector``.'''
        return self.uniforms.get('color', Vector((0, 0, 0)))

    @color.setter
    def color(self, val):
        self.uniforms['color'] = val

'''Post-processing filter that darkens the screen edges with a smooth vignette mask.'''
from .shader import Filter2D
from mathutils import Vector


glsl = """
uniform sampler2D bgl_RenderedTexture;

// in vec4 bgl_TexCoord;
uniform float power;
uniform vec3 color;

// out vec4 fragColor;

void main()
{
	vec2 uv = bgl_TexCoord.xy;
    uv *=  1.0 - uv.yx;
    float vig = uv.x * uv.y * 15;
    vig = pow(vig, power);
    vec4 vcol = vec4(color.x, color.y, color.z, 1);
    vec4 px = texture(bgl_RenderedTexture, bgl_TexCoord.xy);

    fragColor = mix(vcol, px, vig);
}
"""


class Vignette(Filter2D):
    '''Vignette filter that mixes the rendered frame with a flat edge ``color`` using a
    smooth radial mask, darkening the corners and borders of the screen.

    :param power: Vignette falloff exponent controlling the sharpness of the edge
        darkening (higher values produce a sharper, more abrupt transition).
    :param color: RGB colour used for the vignette edges (default black ``(0, 0, 0)``).
    :param idx: Filter pass index; passed directly to ``Filter2D``.
    '''

    def __init__(self, power: float = 0.25, color=(0., 0., 0.), idx: int = None) -> None:
        self.uniforms = {'power': float(power), 'color': Vector(color)}
        super().__init__(glsl, idx, {'power': self.uniforms, 'color': self.uniforms})

    @property
    def power(self):
        '''Falloff exponent controlling the sharpness of the vignette edge transition.'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = val

    @property
    def color(self):
        '''RGB colour blended into the screen edges to create the vignette effect.'''
        return self.uniforms['color']

    @color.setter
    def color(self, val):
        if not isinstance(val, Vector):
            val = Vector(val)
        self.uniforms['color'] = val

'''Post-processing filter that converts the rendered frame towards grayscale using BT.601 luminance weights.'''
from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

// in vec4 bgl_TexCoord;
uniform float power;

// out vec4 fragColor;

void main()
{
    float pow = clamp(1.0 - power, 0.0, 1.0);
	vec4 px =  texture(bgl_RenderedTexture, bgl_TexCoord.xy);
	float grey = 0.21 * px.r + 0.71 * px.g + 0.07 * px.b;
	fragColor = vec4(
        px.r * pow + grey * (1.0 - pow),
        px.g * pow + grey * (1.0 - pow),
        px.b * pow + grey * (1.0 - pow),
        1.0
    );
}
"""


class Grayscale(Filter2D):
    '''Grayscale filter that blends the rendered frame with its BT.601 luminance value.

    At ``power=1.0`` the output is fully grey; at ``power=0.0`` the original colours
    are preserved unchanged.

    :param power: Desaturation strength (``0.0`` = no effect, ``1.0`` = fully grey).
    :param idx: Filter pass index; passed directly to ``Filter2D``.
    '''

    def __init__(self, power: float = 1.0, idx: int = None) -> None:
        self.uniforms = {'power': float(power)}
        super().__init__(glsl, idx, {'power': self.uniforms})

    @property
    def power(self):
        '''Desaturation blend factor; ``1.0`` produces a fully grey output.'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = val

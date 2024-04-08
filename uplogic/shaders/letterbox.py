from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

in vec4 bgl_TexCoord;
uniform float power;
uniform float factor;

out vec4 fragColor;

void main()
{
    float pow = clamp(power, 0.0, 1.0);
	vec4 px =  texture(bgl_RenderedTexture, bgl_TexCoord.xy);
    bool cutoff = (bgl_TexCoord.y > 1.0-factor || bgl_TexCoord.y < factor);

    fragColor = mix(
        px,
        vec4(0.0, 0.0, 0.0, 1.0),
        (cutoff ? 1.0 : 0.0) * pow
    );
}
"""


class Letterbox(Filter2D):

    def __init__(self, power: float = 1.0, factor: float = 0.1, idx: int = None) -> None:
        self.settings = {'power': float(power), 'factor': float(factor)}
        super().__init__(glsl, idx, {'power': self.settings, 'factor': self.settings})

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = float(val)
    
    @property
    def factor(self):
        return self.settings['factor']

    @factor.setter
    def factor(self, val):
        self.settings['factor'] = float(val)

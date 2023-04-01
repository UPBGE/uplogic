from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

in vec4 bgl_TexCoord;
uniform float power;

out vec4 fragColor;

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

    def __init__(self, power: float = 1.0, idx: int = None) -> None:
        self.settings = {'power': float(power)}
        super().__init__(glsl, idx, {'power': self.settings, 'color': self.settings})

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = val

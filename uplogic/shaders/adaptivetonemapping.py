from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;
in vec4 bgl_TexCoord;

uniform float avgL;
uniform float power;

out vec4 fragColor;

// vec2 texcoord = vec2(bgl_TexCoord[0]).st;

void main(void)
{
    float contrast = avgL;
    float brightness = avgL * power;
    vec4 value = texture(bgl_RenderedTexture, bgl_TexCoord.xy);
    fragColor = (value/contrast) - brightness;
}"""


class AdaptiveToneMapping(Filter2D):

    def __init__(self, power=1.0, avgL=2.0, idx: int = None) -> None:
        self.uniforms = {'power': float(power), 'avgL': float(avgL)}
        super().__init__(glsl, idx, {'power': self.uniforms, 'avgL': self.uniforms})

    @property
    def power(self):
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = float(val)
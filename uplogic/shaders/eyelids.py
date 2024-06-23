from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

in vec4 bgl_TexCoord;
uniform float power;
uniform float factor;

out vec4 fragColor;

float map_range(float value, float in_min, float in_max, float out_min, float out_max){
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void main()
{
    float transitionArea = .1f;
    float pow = clamp(power, 0.0, 1.0);
	vec4 px =  texture(bgl_RenderedTexture, bgl_TexCoord.xy);

    float bend_factor = 1.0f;

    float y_offset = abs(bgl_TexCoord.x - 0.5) * bend_factor;
    y_offset *= y_offset;
    y_offset *= abs(bgl_TexCoord.y - 0.5);

    float max_y_offset = .5 * .5 * bend_factor;

    float fac_top = clamp(map_range(bgl_TexCoord.y + y_offset, 1.0-factor + transitionArea + max_y_offset, 1.0-factor + transitionArea, 1, 0), 0, 1);
    float fac_bottom = clamp(map_range(bgl_TexCoord.y - y_offset, factor - transitionArea - max_y_offset, factor - transitionArea, 1, 0), 0, 1);

    fragColor = mix(
        px,
        vec4(0.0, 0.0, 0.0, 1.0),
        fac_bottom + fac_top
    );
}
"""


class Eyelids(Filter2D):

    def __init__(self, power: float = 1.0, factor: float = 0.1, idx: int = None) -> None:
        self.uniforms = {'power': float(power), 'factor': float(factor)}
        super().__init__(glsl, idx, {'power': self.uniforms, 'factor': self.uniforms})

    @property
    def power(self):
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = float(val)
    
    @property
    def factor(self):
        return self.uniforms['factor']

    @factor.setter
    def factor(self, val):
        self.uniforms['factor'] = float(val)

from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

// in vec4 bgl_TexCoord;
uniform float power;
uniform float factor;

// out vec4 fragColor;

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
    '''Post-processing filter that masks the screen with curved black eyelid shapes.

    The top and bottom of the screen are covered by a curved black gradient that
    simulates closing eyelids.  The curvature of each lid is derived from a
    barrel-distortion factor tied to the horizontal screen position.

    :param power: Blend weight of the lid mask.  ``0`` leaves the frame
        untouched; ``1`` applies the mask at full strength.  Defaults to
        ``1.0``.
    :param factor: Fraction of the screen height hidden by each eyelid (top
        and bottom independently).  Defaults to ``0.1``.
    :param idx: Render-pass index used to order filters in the pipeline.
    '''

    def __init__(self, power: float = 1.0, factor: float = 0.1, idx: int = None) -> None:
        self.uniforms = {'power': float(power), 'factor': float(factor)}
        super().__init__(glsl, idx, {'power': self.uniforms, 'factor': self.uniforms})

    @property
    def power(self):
        '''Blend weight of the lid mask (``0`` = no mask, ``1`` = full mask).'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = float(val)

    @property
    def factor(self):
        '''Fraction of the screen hidden by each eyelid (top and bottom).'''
        return self.uniforms['factor']

    @factor.setter
    def factor(self, val):
        self.uniforms['factor'] = float(val)

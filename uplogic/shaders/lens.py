from uplogic.shaders.shader import Filter2D

glsl = """
uniform sampler2D bgl_RenderedTexture;
// in vec4 bgl_TexCoord;
// out vec4 fragColor;

uniform float power;

void main(void)
{
    vec2 screen_center = vec2(.5, .5);
    float r = length(bgl_TexCoord.xy - screen_center) * 2;
    vec2 direction = normalize(screen_center - bgl_TexCoord.xy);
    float factor = r*(1-power*(r*r));
    vec2 coords = screen_center - direction * .5 * factor;
    vec4 color = texture(bgl_RenderedTexture, coords);
    if (coords.x <= 0.0 || coords.x >= 1.0 || coords.y <= 0.0 || coords.y >= 1.0) {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }
    fragColor = color;
}"""



class Lens(Filter2D):
    '''Post-processing filter that applies barrel or pincushion lens distortion.

    Pixels are remapped radially outward from the screen centre according to
    ``power``.  Positive values produce pincushion distortion (edges pulled
    inward) while negative values produce barrel distortion (edges pushed
    outward).  Pixels that map outside the ``[0, 1]`` UV range are filled
    with black.  A value of ``0`` disables the effect entirely.

    :param power: Distortion strength.  Positive = pincushion, negative =
        barrel, ``0`` = no distortion.  Defaults to ``0.0``.
    :param idx: Render-pass index used to order filters in the pipeline.
    '''

    def __init__(self, power=0.0, idx: int = None) -> None:
        self.uniforms = {'power': float(power)}
        super().__init__(glsl, idx, {'power': self.uniforms})

    @property
    def power(self):
        '''Lens distortion strength (positive = pincushion, negative = barrel).'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = float(val)

from .shader import Filter2D

glsl = """
uniform sampler2D bgl_RenderedTexture;
in vec4 bgl_TexCoord;
out vec4 fragColor;

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

    def __init__(self, power=0.0, idx: int = None) -> None:
        self.settings = {'power': float(power)}
        super().__init__(glsl, idx, {'power': self.settings})

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = float(val)

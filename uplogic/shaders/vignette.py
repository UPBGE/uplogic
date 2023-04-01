from .shader import Filter2D
from mathutils import Vector


glsl = """
uniform sampler2D bgl_RenderedTexture;

in vec4 bgl_TexCoord;
uniform float power;
uniform vec3 color;

out vec4 fragColor;

void main( )
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

    def __init__(self, power: float = 0.25, color=(0., 0., 0.), idx: int = None) -> None:
        self.settings = {'power': float(power), 'color': Vector(color)}
        super().__init__(glsl, idx, {'power': self.settings, 'color': self.settings})

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = val

    @property
    def color(self):
        return self.settings['color']

    @color.setter
    def color(self, val):
        if not isinstance(val, Vector):
            val = Vector(val)
        self.settings['color'] = val

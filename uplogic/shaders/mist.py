from .shader import ULFilter
from mathutils import Vector


glsl = """
uniform sampler2D bgl_RenderedTexture;
uniform sampler2D bgl_DepthTexture;
in vec4 bgl_TexCoord;

uniform float power;
uniform vec3 color;
uniform float start;
uniform float end;

out vec4 fragColor;

vec4 lerp(vec4 a, vec4 b, float fac){
    return (fac * b) + ((1 - fac) * a);
}

float linearize_depth(vec2 uv){
    float n = start;
    float f = end;
    float z = texture(bgl_DepthTexture, uv).x;
    return (2.0 * n) / (f + n - z * (f - n));
}

void main(){
    float x = bgl_TexCoord[0];
    float y = bgl_TexCoord[1];
    vec2 coords = vec2(x, y);
    vec4 col = texture(bgl_RenderedTexture, coords);
    float d = linearize_depth(coords);
    vec4 black = vec4(0, 0, 0, 1);
    vec4 shade = vec4(color.x, color.y, color.z, 1);
    vec4 depth = vec4(d, d, d, 1);
    depth = depth * shade;
    col = lerp(col, depth, d * power);
    fragColor = col;
}
"""


class Mist(ULFilter):

    def __init__(self, start=.1, end=50.0, color=(0.5, 0.7, 0.9), power=1.0, idx: int = None) -> None:
        self.settings = {
            'start': float(start),
            'end': float(end),
            'color': Vector(color),
            'power': float(power)
        }
        super().__init__(glsl, idx, {
            'start': self.settings,
            'end': self.settings,
            'color': self.settings,
            'power': self.settings
        })

    @property
    def start(self):
        return self.settings['start']
    
    @start.setter
    def start(self, val):
        self.settings['start'] = float(val)

    @property
    def end(self):
        return self.settings['end']
    
    @end.setter
    def end(self, val):
        self.settings['end'] = float(val)
    
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
'''Post-processing filter that simulates lens chromatic aberration by separating RGB channels.'''
from .shader import Filter2D

glsl = """
uniform sampler2D bgl_RenderedTexture;
// in vec4 bgl_TexCoord;

uniform float power;

// out vec4 fragColor;

void main()
{
   vec2 texcoord = bgl_TexCoord.xy;
   vec3 sum = vec3(0.0);
   vec3 distance = vec3(1.0-(power*0.01), 1.0-(power*0.02), 1.0-(power*0.03));

   sum.r = vec3(texture(bgl_RenderedTexture, (texcoord -vec2(0.5,0.5)) * distance[0] + vec2(0.5,0.5))).r;
   sum.g = vec3(texture(bgl_RenderedTexture, (texcoord -vec2(0.5,0.5)) * distance[1] + vec2(0.5,0.5))).g;
   sum.b = vec3(texture(bgl_RenderedTexture, (texcoord -vec2(0.5,0.5)) * distance[2] + vec2(0.5,0.5))).b;

   fragColor = vec4(sum, 1.0);
}
"""


class ChromaticAberration(Filter2D):
    '''Chromatic aberration filter that samples the red, green, and blue channels at
    progressively different zoom levels away from the screen centre, replicating the
    colour fringing produced by real lenses.

    :param power: Separation strength; higher values increase the distance between
        channel samples and produce stronger colour fringing at the edges.
    :param idx: Filter pass index; passed directly to ``Filter2D``.
    '''

    def __init__(self, power: float = 2.0, idx: int = None) -> None:
        self.uniforms = {'power': float(power)}
        super().__init__(glsl, idx, {'power': self.uniforms})

    @property
    def power(self):
        '''Channel separation strength; higher values push RGB samples further apart.'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = val

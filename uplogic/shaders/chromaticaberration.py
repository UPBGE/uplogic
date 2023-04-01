from .shader import Filter2D

glsl = """
uniform sampler2D bgl_RenderedTexture;
in vec4 bgl_TexCoord;

uniform float power;

void main()
{
   vec2 texcoord = bgl_TexCoord.xy;
   vec3 sum = vec3(0.0);
   vec3 distance = vec3(1.0-(power*0.01), 1.0-(power*0.02), 1.0-(power*0.03));

   sum.r = vec3(texture(bgl_RenderedTexture, (texcoord -vec2(0.5,0.5)) * distance[0] + vec2(0.5,0.5))).r;
   sum.g = vec3(texture(bgl_RenderedTexture, (texcoord -vec2(0.5,0.5)) * distance[1] + vec2(0.5,0.5))).g;
   sum.b = vec3(texture(bgl_RenderedTexture, (texcoord -vec2(0.5,0.5)) * distance[2] + vec2(0.5,0.5))).b;

   gl_FragColor = vec4(sum, 1.0);
}
"""


class ChromaticAberration(Filter2D):

    def __init__(self, power: float = 2.0, idx: int = None) -> None:
        self.settings = {'power': float(power)}
        super().__init__(glsl, idx, {'power': self.settings})

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = val

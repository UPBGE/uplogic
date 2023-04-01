from .shader import Filter2D


glsl = """
/* Original Code by existical @shadertoy: https://www.shadertoy.com/view/Xltfzj
Modified by Iza Zed for UPBGE
*/

uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
vec2 resolution = vec2(bgl_RenderedTextureWidth, bgl_RenderedTextureHeight);

out vec4 fragColor;
in vec4 bgl_TexCoord;

vec2 texcoord = bgl_TexCoord.xy;

uniform float samples;
uniform float power;

void main()
{
    float Pi = 6.28318530718;

    float quality = 3.0;
   
    vec2 radius = power/resolution.xy;
    
    vec2 uv = texcoord;

    vec4 color = texture(bgl_RenderedTexture, uv);
    
    // Blur calculations
    for( float d=0.0; d<Pi; d+=Pi/samples)
    {
		for(float i=1.0/quality; i<=1.0; i+=1.0/quality)
        {
			color += texture(bgl_RenderedTexture, uv+vec2(cos(d),sin(d)) * radius * i);
        }
    }
    color /= quality * samples - 15.0;
    fragColor = color;
}"""

class Blur(Filter2D):

    def __init__(self, samples=16, power=1.0, idx: int = None) -> None:
       self.settings = {'samples': float(samples), 'power': float(power)}
       super().__init__(glsl, idx, {'samples': self.settings, 'power': self.settings})

    @property
    def samples(self):
        return self.settings['samples']

    @samples.setter
    def samples(self, val):
        self.settings['samples'] = float(val)

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = float(val)

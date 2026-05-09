'''Post-processing filter that applies a radial Gaussian-style blur by sampling in a ring pattern.'''
from .shader import Filter2D


glsl = """
/* Original Code by existical @shadertoy: https://www.shadertoy.com/view/Xltfzj
Modified by Iza Zed for UPBGE
*/

uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
vec2 resolution = vec2(bgl_RenderedTextureWidth, bgl_RenderedTextureHeight);

// out vec4 fragColor;
// in vec4 bgl_TexCoord;

vec2 texcoord = bgl_TexCoord.xy;

uniform float samples;
uniform float power;

void main()
{
    float Pi = 6.28318530718;

    float quality = 9.0;

    vec2 radius = power / resolution.xy;

    vec2 uv = texcoord;

    vec4 color = texture(bgl_RenderedTexture, uv);

    // Blur calculations
    for (float d = 0.0; d < Pi; d += Pi / samples)
    {
		for(float i = 1.0 / quality; i <= 1.0; i += 1.0 / quality)
        {
			color += texture(bgl_RenderedTexture, uv + vec2(cos(d), sin(d)) * radius * i);
        }
    }
    color /= quality;
    fragColor = color;
}"""


class Blur(Filter2D):
    '''Radial blur filter that samples the rendered texture in a ring pattern around each pixel.

    The blur accumulates ``samples`` angular directions over a full 360-degree sweep,
    stepping outward in 9 increments up to the radius defined by ``power``.

    :param power: Blur radius in pixels; larger values produce a wider, softer blur.
    :param samples: Number of angular sample directions per ring (higher values produce
        a smoother result at the cost of performance).
    :param idx: Filter pass index; passed directly to ``Filter2D``.
    '''

    def __init__(self, power=1.0, samples=16, idx: int = None) -> None:
       self.uniforms = {'samples': float(samples), 'power': float(power)}
       super().__init__(glsl, idx, {'samples': self.uniforms, 'power': self.uniforms})

    @property
    def samples(self):
        '''Number of angular sample directions taken around each ring of the blur.'''
        return self.uniforms['samples']

    @samples.setter
    def samples(self, val):
        self.uniforms['samples'] = float(val)

    @property
    def power(self):
        '''Blur radius in pixels controlling how far samples are spread from the centre.'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = float(val)

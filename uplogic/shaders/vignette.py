from .shader import ULFilter


vignette = """
uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
in vec4 bgl_TexCoord;
uniform float power;

out vec4 fragColor;

void main( )
{
	vec2 uv = bgl_TexCoord.xy; // / vec2(bgl_RenderedTextureWidth, bgl_RenderedTextureHeight);
    uv *=  1.0 - uv.yx;
    float vig = uv.x * uv.y * 15;
    vig = pow(vig, power);

    fragColor = texture2D(bgl_RenderedTexture, bgl_TexCoord.xy) * vig; 
}
"""


class Vignette(ULFilter):

    def __init__(self, idx: int = None) -> None:
        self.settings = {'power': 0.0}
        super().__init__(vignette, idx, {'power': self.settings})
    
    @property
    def power(self):
        return self.settings['power']
    
    @power.setter
    def power(self, val):
        self.settings['power'] = val

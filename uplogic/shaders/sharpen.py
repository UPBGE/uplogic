from .shader import Filter2D
from bge import logic


glsl = """
#version 120
#pragma optionNV(fastmath on)
#pragma optionNV(fastprecision on)
#pragma optionNV(inline all)
#pragma optionNV(unroll all)
#pragma optionNV(ifcvt none)
#pragma optionNV(strict on)

uniform float sharpness;

uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;

in vec4 bgl_TexCoord;

out vec4 fragColor;

void main(void)
{
    float width = 1.0 /  bgl_RenderedTextureWidth; 
    float height = 1.0 / bgl_RenderedTextureHeight;

    vec4 Total = vec4(0.0);

    vec2 Scoord = bgl_TexCoord.xy;
    vec4 Msample = texture(bgl_RenderedTexture, Scoord);

    float Hoffs = 1.5 * width;
    float Voffs = 1.5 * height;

    vec2 UV1 = bgl_TexCoord.xy + vec2(Hoffs,Voffs);  
    Total += texture(bgl_RenderedTexture, UV1);

    vec2 UV2 = bgl_TexCoord.xy + vec2(-Hoffs,Voffs);  
    Total += texture(bgl_RenderedTexture, UV2);

    vec2 UV3 = bgl_TexCoord.xy + vec2(-Hoffs,-Voffs);  
    Total += texture(bgl_RenderedTexture, UV3);

    vec2 UV4 = bgl_TexCoord.xy + vec2(Hoffs,-Voffs);  
    Total += texture(bgl_RenderedTexture, UV4);

    Total *= .15;

    Hoffs = 2.5 * width;
    Voffs = 2.5 * height;

    vec2 UV5 = bgl_TexCoord.xy + vec2(Hoffs,0.0);  
    Total += texture(bgl_RenderedTexture, UV5) *.1;

    vec2 UV6 = bgl_TexCoord.xy + vec2(0.0,Voffs);  
    Total += texture(bgl_RenderedTexture, UV6) *.1;

    vec2 UV7 = bgl_TexCoord.xy + vec2(-Hoffs,0.0);  
    Total += texture(bgl_RenderedTexture, UV7) *.1;

    vec2 UV8 = bgl_TexCoord.xy + vec2(0.0,-Voffs);  
    Total += texture(bgl_RenderedTexture, UV8) *.1;

    vec4 Final = (1 + sharpness) * Msample - Total * sharpness;

    fragColor.xyz = Final.xyz;
    fragColor.a = 1.0;
}
"""


class Sharpen(Filter2D):

    def __init__(self, sharpness=0.0, idx: int = None) -> None:
        self.settings = {'sharpness': float(sharpness)}
        super().__init__(glsl, idx, {'sharpness': self.settings})

    @property
    def sharpness(self):
        return self.settings['sharpness']

    @sharpness.setter
    def sharpness(self, val):
        self.settings['sharpness'] = val

from .shader import ULFilter


fxaa = """
uniform sampler2D bgl_RenderedTexture;
in vec4 bgl_TexCoord;
uniform float brightness;

out vec4 fragColor;

void main() {
    fragColor = texture2D(bgl_RenderedTexture, bgl_TexCoord.xy) * brightness;
}
"""


class Brightness(ULFilter):

    def __init__(self, idx: int = None) -> None:
        self.settings = {'brightness': 1.0}
        super().__init__(fxaa, idx, {'brightness': self.settings})
    
    @property
    def brightness(self):
        return self.settings['brightness']
    
    @brightness.setter
    def brightness(self, val):
        self.settings['brightness'] = val

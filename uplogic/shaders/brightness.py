from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;
in vec4 bgl_TexCoord;
uniform float brightness;

out vec4 fragColor;

void main() {
    fragColor = texture(bgl_RenderedTexture, bgl_TexCoord.xy) * brightness;
}
"""


class Brightness(Filter2D):

    def __init__(self, brightness=1.0, idx: int = None) -> None:
        self.settings = {'brightness': float(brightness)}
        super().__init__(glsl, idx, {'brightness': self.settings})

    @property
    def brightness(self):
        return self.settings['brightness']

    @brightness.setter
    def brightness(self, val):
        self.settings['brightness'] = float(val)

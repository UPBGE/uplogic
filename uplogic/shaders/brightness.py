'''Post-processing filter that scales the rendered frame by a uniform brightness multiplier.'''
from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;
// in vec4 bgl_TexCoord;
uniform float brightness;

// out vec4 fragColor;

void main() {
    fragColor = texture(bgl_RenderedTexture, bgl_TexCoord.xy) * brightness;
}
"""


class Brightness(Filter2D):
    '''Simple screen-multiply brightness filter that computes ``output = input * brightness``.

    :param brightness: Multiply factor applied to every pixel (``1.0`` = no change,
        ``>1.0`` = brighter, ``<1.0`` = darker).
    :param idx: Filter pass index; passed directly to ``Filter2D``.
    '''

    def __init__(self, brightness=1.0, idx: int = None) -> None:
        self.uniforms = {'brightness': float(brightness)}
        super().__init__(glsl, idx, {'brightness': self.uniforms})

    @property
    def brightness(self):
        '''Screen multiply factor applied to every pixel colour.'''
        return self.uniforms['brightness']

    @brightness.setter
    def brightness(self, val):
        self.uniforms['brightness'] = float(val)

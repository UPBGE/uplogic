from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

in vec4 bgl_TexCoord;
uniform float gamma;
out vec4 fragColor;

void main()
{
    fragColor = pow(texture(bgl_RenderedTexture, bgl_TexCoord.xy), vec4(gamma)) * pow(1, 2);
}
"""


class Buffer(Filter2D):

    def __init__(self, gamma=1, exposure=0, idx: int = None) -> None:
        self.settings = {'gamma': float(gamma)}
        super().__init__(glsl, idx, {'gamma': self.settings})
        self._filter.addOffScreen(0)

    @property
    def bindcode(self):
        return self._filter.offScreen.colorBindCodes[0]

    @property
    def texture(self):
        return self._filter.offScreen.getColorTexture()

    @property
    def depth_texture(self):
        return self._filter.offScreen.getDepthTexture()


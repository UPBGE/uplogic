from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

in vec4 bgl_TexCoord;
uniform float gamma;
out vec4 fragColor;

void main()
{
    fragColor = pow(texture(bgl_RenderedTexture, bgl_TexCoord.xy), vec4(gamma));
}
"""


class Buffer(Filter2D):

    def __init__(self, gamma=.5, idx: int = 99) -> None:
        self.settings = {'gamma': float(gamma)}
        super().__init__(glsl, idx, {'gamma': self.settings})
        self._filter.addOffScreen(0)

    @property
    def bindcode(self):
        return self._filter.offScreen.colorBindCodes[0]

    @property
    def texture(self):
        return self._filter.offScreen.getColorTexture()


depth_glsl = """
uniform sampler2D bgl_DepthTexture;

in vec4 bgl_TexCoord;
uniform float gamma;
out vec4 fragColor;

void main()
{
    fragColor = pow(texture(bgl_DepthTexture, bgl_TexCoord.xy), vec4(gamma));
}
"""


class DepthBuffer(Buffer):

    def __init__(self, gamma=1, idx: int = None) -> None:
        self.settings = {'gamma': float(gamma)}
        super().__init__(depth_glsl, idx, {'gamma': self.settings})
        self._filter.addOffScreen(0)


'''Off-screen color and depth buffer filters for BGE post-processing.

Provides :class:`Buffer` and :class:`DepthBuffer`, both thin subclasses of
:class:`~uplogic.shaders.shader.Filter2D` that render the current frame to an
off-screen framebuffer with optional gamma correction.
'''
from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

// in vec4 bgl_TexCoord;
// out vec4 fragColor;
uniform float gamma;

void main()
{
    fragColor = pow(texture(bgl_RenderedTexture, bgl_TexCoord.xy), vec4(gamma));
}
"""


class Buffer(Filter2D):
    '''Off-screen color buffer that captures the rendered scene with gamma correction.

    Wraps :class:`~uplogic.shaders.shader.Filter2D` and samples
    ``bgl_RenderedTexture``. After construction ``addOffScreen(0)`` is called
    to attach an off-screen framebuffer. The ``gamma`` uniform raises or lowers
    scene brightness before the result is stored in the buffer.

    :param gamma: Gamma exponent applied to each colour channel before storage.
        A value of ``1`` leaves brightness unchanged.
    :param idx: Pass index to assign; ``None`` lets :class:`~uplogic.shaders.shader.FilterSystem`
        auto-assign the lowest free index.
    '''

    def __init__(self, gamma=1, idx: int = None) -> None:
        self.uniforms = {'gamma': float(gamma)}
        super().__init__(glsl, idx, {'gamma': self.uniforms})
        self._filter.addOffScreen(0)

    @property
    def bindcode(self):
        '''Raw OpenGL texture bind code of the off-screen color attachment.

        :returns: The integer bind code from ``offScreen.colorBindCodes[0]``.
        '''
        return self._filter.offScreen.colorBindCodes[0]

    @property
    def texture(self):
        '''``gpu.types.GPUTexture`` of the off-screen color attachment.

        :returns: The ``GPUTexture`` obtained via ``offScreen.getColorTexture()``.
        '''
        return self._filter.offScreen.getColorTexture()


depth_glsl = """
uniform sampler2D bgl_DepthTexture;

// in vec4 bgl_TexCoord;
// out vec4 fragColor;
uniform float gamma;

void main()
{
    fragColor = pow(texture(bgl_DepthTexture, bgl_TexCoord.xy), vec4(gamma));
}
"""


class DepthBuffer(Buffer):
    '''Off-screen depth buffer variant that samples ``bgl_DepthTexture``.

    Behaves identically to :class:`Buffer` but uses the scene depth texture
    as the source instead of the rendered colour texture. Gamma correction is
    still applied via the ``gamma`` uniform.

    :param gamma: Gamma exponent applied to each depth sample before storage.
    :param idx: Pass index to assign; ``None`` lets :class:`~uplogic.shaders.shader.FilterSystem`
        auto-assign the lowest free index.
    '''

    def __init__(self, gamma=1, idx: int = None) -> None:
        self.uniforms = {'gamma': float(gamma)}
        super().__init__(depth_glsl, idx, {'gamma': self.uniforms})
        self._filter.addOffScreen(0)

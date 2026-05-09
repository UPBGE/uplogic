from .shader import Filter2D


glsl = """
uniform sampler2D bgl_RenderedTexture;

// in vec4 bgl_TexCoord;
uniform float power;
uniform float factor;

// out vec4 fragColor;

void main()
{
    float pow = clamp(power, 0.0, 1.0);
	vec4 px =  texture(bgl_RenderedTexture, bgl_TexCoord.xy);
    bool cutoff = (bgl_TexCoord.y > 1.0-factor || bgl_TexCoord.y < factor);

    fragColor = mix(
        px,
        vec4(0.0, 0.0, 0.0, 1.0),
        (cutoff ? 1.0 : 0.0) * pow
    );
}
"""


class Letterbox(Filter2D):
    '''Post-processing filter that adds cinematic horizontal black bars.

    Horizontal black bars are composited at the top and bottom of the frame
    to simulate a widescreen letterbox.  The bars use a slight barrel curve
    at the edges controlled by the GLSL curve factor.

    :param power: Opacity of the black bars in the range ``0``–``1``.
        ``0`` leaves the frame untouched; ``1`` renders fully opaque bars.
        Defaults to ``1.0``.
    :param factor: Fraction of the screen height occupied by each bar
        (top and bottom independently) in the range ``0``–``0.5``.
        Defaults to ``0.1``.
    :param idx: Render-pass index used to order filters in the pipeline.
    '''

    def __init__(self, power: float = 1.0, factor: float = 0.1, idx: int = None) -> None:
        self.uniforms = {'power': float(power), 'factor': float(factor)}
        super().__init__(glsl, idx, {'power': self.uniforms, 'factor': self.uniforms})

    @property
    def power(self):
        '''Bar opacity (``0`` = transparent, ``1`` = fully black).'''
        return self.uniforms['power']

    @power.setter
    def power(self, val):
        self.uniforms['power'] = float(val)

    @property
    def factor(self):
        '''Height fraction for the top and bottom bars (``0``–``0.5``).'''
        return self.uniforms['factor']

    @factor.setter
    def factor(self, val):
        self.uniforms['factor'] = float(val)

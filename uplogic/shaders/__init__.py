'''2D post-processing filter (shader) library for uplogic.

All filters subclass :class:`~uplogic.shaders.Filter2D` and are registered
with the :class:`~uplogic.shaders.shader.FilterSystem` on construction, so
simply instantiating one is enough to activate it.

Typical usage::

    from uplogic import shaders

    vignette = shaders.Vignette(power=0.3, color=(0, 0, 0))
    bloom = shaders.Blur(power=2.0, samples=16)
    ao = shaders.SSAO(power=0.8)

    # adjust at runtime
    vignette.power = 0.5
    ao.active = False        # disable without removing
'''

from .shader import Filter2D
from .buffer import Buffer
from .fxaa import FXAA
from .brightness import Brightness
from .vignette import Vignette
from .grayscale import Grayscale
from .adaptivetonemapping import AdaptiveToneMapping
from .hbao import HBAO
from .ssao import SSAO
from .mist import Mist
from .levels import Levels
from .letterbox import Letterbox
from .distort import Distort
from .droplets import Droplets
from .blur import Blur
from .dof import DoF
from .lens import Lens
from .texture import Texture
from .texture import Mask
from .chromaticaberration import ChromaticAberration
from .sharpen import Sharpen
from .splitscreen import SplitScreen
from .eyelids import Eyelids
from .shader import load_glsl
from .shader import remove_filter
from .shader import toggle_filter
from .shader import set_filter_state
from .shader import uniforms

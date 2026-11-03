'''Off-screen render target widget for uplogic UI.'''

from .widget import Widget
import gpu
import bge, bpy
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d
from mathutils import Vector
from bge import render
from uplogic.shaders import Buffer


_VERTEX_SOURCE = '''
    void main() {
        uv = texCoord;
        gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0, 1.0);
    }
'''

_FRAGMENT_SOURCE = '''
    void main() {
        fragColor = texture(renderedTexture, uv);
    }
'''

_shader = None
'''Pass-through shader shared by all :class:`RenderedTexture` widgets.

Compiled once and never freed: dropping a ``GPUShader`` that is still bound
leaves the GPU context pointing at freed memory, which crashes in Blender 5.2+
the next time an image texture generates mipmaps.
'''


def _get_shader():
    global _shader
    if _shader is None:
        info = gpu.types.GPUShaderCreateInfo()
        info.vertex_in(0, 'VEC2', 'texCoord')
        info.vertex_in(1, 'VEC2', 'pos')
        uv_out = gpu.types.GPUStageInterfaceInfo('rendered_texture_interface')
        uv_out.smooth('VEC2', 'uv')
        info.vertex_out(uv_out)
        info.push_constant('MAT4', 'ModelViewProjectionMatrix')
        info.sampler(0, 'FLOAT_2D', 'renderedTexture')
        info.fragment_out(0, 'VEC4', 'fragColor')
        info.vertex_source(_VERTEX_SOURCE)
        info.fragment_source(_FRAGMENT_SOURCE)
        _shader = gpu.shader.create_from_info(info)
    return _shader


class RenderedTexture(Widget):
    '''Widget that blits an off-screen render :class:`~uplogic.shaders.Buffer`
    into the canvas.

    Allocates a ``GPUOffScreen`` sized to the widget's draw dimensions and
    renders the ``Buffer`` texture into it using a custom pass-through shader.
    No constructor parameters are required; position and size are inherited
    from the parent widget.
    '''

    def __init__(self):
        super().__init__()
        self.buffer = Buffer()
        self.start()

    def _build_shader(self, force=False):
        pos = self._draw_pos
        size = self._draw_size
        x0 = Vector((pos[0], pos[1]))
        x1 = Vector((pos[0] + size[0], pos[1]))
        y1 = Vector((pos[0] + size[0], pos[1] + size[1]))
        y0 = Vector((pos[0], pos[1] + size[1]))

        vertices = self._vertices = (
            x1, x0, y1, y0
        )

        self._shader = _get_shader()
        self._batch = batch_for_shader(
            self._shader, 'TRI_STRIP',
            {
                "pos": vertices,
                "texCoord": (
                    (.9999, .0001),
                    (.0001, .0001),
                    (.9999, .9999),
                    (.0001, .9999)
                ),
            },
        )

    def draw(self):
        self._shader.uniform_sampler("renderedTexture", self.buffer.texture)
        self._setup_draw()
        self._batch.draw(self._shader)
        super().draw()

from .widget import Widget
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from uplogic.shaders import Buffer


class RenderedTexture(Widget):

    def __init__(self):
        super().__init__()
        self.buffer = Buffer()

    def _build_shader(self):
        size = self._draw_size
        self.view = gpu.types.GPUOffScreen(size[0], size[1])

        pos = self._draw_pos
        size = self._draw_size
        x0 = Vector((pos[0], pos[1]))
        x1 = Vector((pos[0] + size[0], pos[1]))
        y1 = Vector((pos[0] + size[0], pos[1] + size[1]))
        y0 = Vector((pos[0], pos[1] + size[1]))

        vertices = self._vertices = (
            x1, x0, y1, y0
        )

        tex_vert_shader = """
        in vec2 texCoord;
        in vec2 pos;
        out vec2 uv;

        uniform mat4 ModelViewProjectionMatrix;

        void main() {
            uv = texCoord;
            gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0, 1.0);
        }
        """

        tex_frag_shader = """
        in vec2 uv;
        out vec4 fragColor;

        uniform sampler2D renderedTexture;

        void main() {
            vec4 image = texture(renderedTexture, uv);
            fragColor = image;
        }
        """
        self.shader = gpu.types.GPUShader(tex_vert_shader, tex_frag_shader)
        self._batch = batch_for_shader(
            self.shader, 'TRI_STRIP',
            {
                "pos": vertices,
                "texCoord": (
                    (.9999, .0001),
                    (0.0001, 0.0001),
                    (.9999, .9999),
                    (.0001, .9999)
                ),
            },
        )


    def draw(self):
        self.shader.uniform_sampler("renderedTexture", self.buffer.texture)
        super()._setup_draw()
        self._batch.draw(self.shader)
        super().draw()

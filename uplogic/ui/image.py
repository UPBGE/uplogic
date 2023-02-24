from .widget import Widget
import gpu
import bge, bpy
from gpu_extras.batch import batch_for_shader


class Image(Widget):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, texture=None):
        super().__init__(pos, size, relative=relative)
        self.texture = texture

    @property
    def texture(self):
        return self._texture
        
    @texture.setter
    def texture(self, val):
        texture = bpy.data.images.get(val)
        if texture:
            self._texture = gpu.texture.from_image(texture)

    def build_shader(self):
        pos = self._draw_pos
        vertices = self.vertices = (
            (pos[0], pos[1]),
            (pos[0] + self.size[0], pos[1]),
            (pos[0] + self.size[0], pos[1] + self.size[1]),
            (pos[0], pos[1] + self.size[1])
        )
        self.shader = gpu.shader.from_builtin('2D_IMAGE')
        self.batch = batch_for_shader(
            self.shader, 'TRI_FAN',
            {
                "pos": vertices,
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )
    
    def draw(self):
        self.shader.bind()
        self.shader.uniform_sampler("image", self.texture)
        self.batch.draw(self.shader)
        super().draw()

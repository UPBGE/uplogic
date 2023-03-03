from .widget import Widget
from uplogic.input import MOUSE
import gpu
import bge, bpy
from gpu_extras.batch import batch_for_shader
from bge import logic


CURSOR = None


def remove_custom_cursor():
    scene = bge.logic.getCurrentScene()
    to_remove = []
    for f in scene.post_draw:
        if f.__name__ == '_draw_custom_cursor':
            to_remove.append(f)
    for f in to_remove:
        scene.post_draw.remove(f)


class Cursor(Widget):

    def __init__(self, size=(20,20), texture=None, offset=(0, 0)):
        self.offset = offset
        remove_custom_cursor()
        super().__init__(MOUSE.position, size)
        self._texture = None
        self.shader = None
        self.texture = texture
        self.pos = MOUSE.position
        self._last_visible = logic.mouse.visible
        bge.logic.getCurrentScene().post_draw.append(self._draw_custom_cursor)

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, val):
        texture = bpy.data.images.get(val)
        if texture:
            self._texture = gpu.texture.from_image(texture)

    def build_shader(self):
        self.shader = gpu.shader.from_builtin('2D_IMAGE')
        screen_res = [bge.render.getWindowWidth(), bge.render.getWindowHeight()]
        mpos = [MOUSE.position.x * screen_res[0] + self.offset[0], (1 - MOUSE.position.y) * screen_res[1] + self.offset[1]]
        self.batch = batch_for_shader(
            self.shader, 'TRI_FAN',
            {
                "pos": (
                    (mpos[0], mpos[1] - self.size[1]),
                    (mpos[0] + self.size[0], mpos[1] - self.size[1]),
                    (mpos[0] + self.size[0], mpos[1]),
                    mpos
                ),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )

    def _draw_custom_cursor(self):
        self.build_shader()
        scene = bge.logic.getCurrentScene()
        if scene.post_draw[-1] is not self._draw_custom_cursor:
            scene.post_draw.remove(self._draw_custom_cursor)
            scene.post_draw.append(self._draw_custom_cursor)
        gpu.state.blend_set('ALPHA')
        if self.show:
            self.pos = MOUSE.position
            self.shader.bind()
            self.shader.uniform_sampler("image", self.texture)
            self.batch.draw(self.shader)

from bge.types import KX_Camera
from gpu.types import GPUOffScreen
from uplogic.ui.widget import Widget
from gpu_extras.presets import draw_texture_2d
import bge
import bpy
import gpu


class Camera(Widget):

    def __init__(self, pos=[0, 0], size=(100, 100), relative={}, camera=None, halign='left', valign='bottom') -> None:
        self.camera = camera
        Widget.__init__(self, pos, size, (0, 0, 0, 0), relative, halign, valign, 0)
        self.start()

    @property
    def parent(self):
        """The widget whose position and size to use relatively."""
        return self._parent

    @parent.setter
    def parent(self, val):
        if self.parent is not val and self.parent:
            self.parent.remove_widget(self)
        if self.use_clipping is None:
            self.use_clipping = val.use_clipping
        self._parent = val
        self.pos = self.pos
        self.size = self.size
        self.camera.useViewport = val is not None and val.show and self.show
        self._build_shader()

    @property
    def camera(self) -> KX_Camera:
        return self._camera

    @camera.setter
    def camera(self, val):
        self._camera = val

    def draw(self):
        self._setup_draw()
        self.camera.useViewport = self.parent is not None and self.parent.show and self.show
        super().draw()

    def _build_shader(self):
        if self.camera is None:
            return
        pos = self._draw_pos
        size = self._draw_size
        self.camera.setViewport(
            round(pos[0]),
            round(pos[1]),
            round(pos[0] + size[0]),
            round(pos[1] + size[1])
        )

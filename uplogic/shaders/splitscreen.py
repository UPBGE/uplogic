from .rendertoscreen import RenderToScreen
from bge.types import KX_Camera
from bge import render, logic
from uplogic.ui import Canvas, Path


class SplitScreen:
    def __init__(self, camera2: KX_Camera = None, camera3: KX_Camera=None, camera4: KX_Camera=None) -> None:
        self.cameras: list[KX_Camera] = []
        # self._canvas = Canvas()
        # self._path_y = Path(relative={'points': True}, points=[(.5, 0), (.5, 1)], line_color=(0, 0, 0, .0), line_width=2)
        # self._path_x = Path(relative={'points': True}, points=[(0, .5), (1, .5)], line_color=(0, 0, 0, .0), line_width=2)
        # self._canvas.add_widget(self._path_y)
        # self._canvas.add_widget(self._path_x)
        cam = self._camera = logic.getCurrentScene().active_camera
        self.add_camera(cam)
        if camera2 is not None:
            self.add_camera(camera2)
        if camera3 is not None:
            self.add_camera(camera3)
        if camera4 is not None:
            self.add_camera(camera4)

    def disable(self):
        for cam in self.cameras:
            cam.useViewport = False
        self._camera.useViewport = False

    def enable(self):
        for cam in self.cameras:
            cam.useViewport = True
        self._arrange()

    def add_camera(self, camera: KX_Camera):
        cameras = self.cameras
        if len(cameras) == 4:
            print('Maximum amount of cameras reached!')
            return
        cameras.append(camera)
        if len(cameras) == 0:
            return
        self._arrange()

    def remove_camera(self, idx=-1):
        if len(self.cameras) == 0:
            return
        cam = self.cameras.pop(idx)
        cam.setViewport(
            -1,
            -1,
            -1,
            -1
        )
        self._arrange()

    def _arrange(self):
        cameras = self.cameras
        cam_amount = len(cameras)
        width = render.getWindowWidth()
        height = render.getWindowHeight()
        offset_x = 0
        offset_y = 0
        # self._path_x.show = False
        # self._path_y.show = False
        if cam_amount > 1:
            # self._path_y.show = True
            width = int(width * .5)
            offset_x = width
        if cam_amount > 2:
            # self._path_x.show = True
            height = int(height * .5)
            offset_y = height

        cameras[0].setViewport(
            0,
            offset_y + 1,
            width,
            offset_y + height
        )
        cameras[0].useViewport = True
        if cam_amount > 1:
            cameras[1].setViewport(
                offset_x + 1,
                offset_y + 1,
                offset_x + width,
                offset_y + height
            )
            cameras[1].useViewport = True
        if cam_amount > 2:
            cameras[2].setViewport(
                0,
                0,
                width,
                height
            )
            cameras[2].useViewport = True
        if cam_amount > 3:
            cameras[3].setViewport(
                offset_x + 1,
                0,
                offset_x + width,
                height
            )
            cameras[3].useViewport = True

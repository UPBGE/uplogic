# from .rendertoscreen import RenderToScreen
from bge.types import KX_Camera
from bge import render, logic
from uplogic import console


class SplitScreen:
    '''Divides the game window into up to four viewports.

    Each viewport is rendered from a different camera. The layout adjusts
    automatically depending on how many cameras are registered:

    - 1 camera  — full-screen (1×1)
    - 2 cameras — side-by-side (1×2)
    - 3–4 cameras — 2×2 grid

    The currently active camera is always added as the first viewport on
    construction. Additional cameras may be supplied via the constructor
    parameters or added later with :meth:`add_camera`.
    '''

    def __init__(self, camera2: KX_Camera = None, camera3: KX_Camera=None, camera4: KX_Camera=None) -> None:
        '''Initialise SplitScreen with up to three additional cameras.

        The currently active ``KX_Camera`` is always registered as the first
        viewport. Optional cameras are appended in the order provided.

        :param camera2: Optional ``KX_Camera`` for the second viewport.
        :param camera3: Optional ``KX_Camera`` for the third viewport.
        :param camera4: Optional ``KX_Camera`` for the fourth viewport.
        '''
        self.cameras: list[KX_Camera] = []
        cam = self._camera = logic.getCurrentScene().active_camera
        self.add_camera(cam)
        if camera2 is not None:
            self.add_camera(camera2)
        if camera3 is not None:
            self.add_camera(camera3)
        if camera4 is not None:
            self.add_camera(camera4)

    def disable(self):
        '''Disable ``useViewport`` on all managed cameras.'''
        for cam in self.cameras:
            cam.useViewport = False
        self._camera.useViewport = False

    def enable(self):
        '''Enable ``useViewport`` on all managed cameras and recalculate viewports.'''
        for cam in self.cameras:
            cam.useViewport = True
        self._arrange()

    def add_camera(self, camera: KX_Camera):
        '''Append a camera and recalculate the viewport arrangement.

        If the four-camera limit has already been reached a warning is logged
        and the method returns without making any changes.

        :param camera: The ``KX_Camera`` to add as an additional viewport.
        '''
        cameras = self.cameras
        if len(cameras) == 4:
            console.warning('Maximum amount of cameras reached!')
            return
        cameras.append(camera)
        if len(cameras) == 0:
            return
        self._arrange()

    def remove_camera(self, idx=-1):
        '''Remove a camera from the list and recalculate viewports.

        The removed camera's viewport is set to an invalid region
        ``(-1, -1, -1, -1)`` so it stops rendering. Does nothing if the
        camera list is empty.

        :param idx: List index of the camera to remove. Defaults to ``-1``
            (the last camera).
        '''
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
        '''Recalculate and apply viewport rectangles for all registered cameras.

        Divides the current window into equal regions based on the number of
        registered cameras: full-screen for one camera, side-by-side for two,
        and a 2×2 grid for three or four. Viewport coordinates are set via
        ``setViewport`` and ``useViewport`` is enabled on each camera.
        '''
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

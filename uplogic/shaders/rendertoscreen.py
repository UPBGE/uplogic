from bge.types import KX_GameObject
from gpu_extras.presets import draw_texture_2d
import bge
import bpy
import gpu


class RenderToScreen:
    '''Renders a Blender camera into a GPU off-screen buffer and blits it to the screen.

    On construction an off-screen framebuffer of the given ``resolution`` is
    created. Every ``interval`` game ticks :meth:`draw` renders the scene from
    the supplied camera's world matrix and projection matrix via
    ``GPUOffScreen.draw_view3d``; the last rendered colour texture is blitted
    to screen-space position ``pos`` every tick.

    Useful for picture-in-picture views or off-screen cameras.
    '''

    def __init__(self, camera: KX_GameObject, resolution=(1920, 1080), pos=(0, 0), interval=1) -> None:
        '''Initialise the RenderToScreen helper.

        Allocates the off-screen buffer, hides Blender overlays, caches the
        camera's projection matrix, registers :meth:`stop` as a ``game_post``
        handler, and appends :meth:`draw` to the current scene's
        ``post_draw`` list.

        :param camera: ``KX_GameObject`` whose ``.blenderObject`` is used as
            the render camera.
        :param resolution: ``(width, height)`` tuple for the off-screen
            framebuffer and the on-screen blit size.
        :param pos: ``(x, y)`` screen-space position of the top-left corner
            of the blitted texture.
        :param interval: Re-render the camera only every ``interval`` ticks.
            The previous image is blitted in between. Rendering the scene a
            second time is expensive, so values of 2-4 save a lot of frame time.
        '''
        self.scene = bpy.data.scenes.get(camera.scene.name, None)
        self.offscreen = None
        if self.scene is None:
            return
        self.camera = camera.blenderObject
        self.resolution = resolution
        self.pos = pos
        self.interval = max(1, int(interval))
        self._tick = 0
        self._has_image = False
        self.offscreen = gpu.types.GPUOffScreen(resolution[0], resolution[1])
        self.update_projection()

        context = bpy.context
        context.space_data.overlay.show_overlays = False
        bpy.app.handlers.game_post.append(self.stop)
        bge.logic.getCurrentScene().post_draw.append(self.draw)

    def update_projection(self):
        '''Recalculate the cached projection matrix.

        Call this after changing the camera's lens, sensor or clipping
        settings, or after changing ``resolution``.
        '''
        width, height = self.resolution
        self.projection_matrix = self.camera.calc_matrix_camera(
            bpy.context.evaluated_depsgraph_get(),
            x=width,
            y=height
        )

    def stop(self, *a):
        '''Restore overlay visibility and release the off-screen buffer.

        Registered as a ``game_post`` handler on construction. Sets
        ``space_data.overlay.show_overlays`` back to ``True``, unregisters
        :meth:`draw` and frees the GPU buffer.
        '''
        context = bpy.context
        context.space_data.overlay.show_overlays = True
        try:
            bge.logic.getCurrentScene().post_draw.remove(self.draw)
        except (ValueError, AttributeError):
            pass
        if self.stop in bpy.app.handlers.game_post:
            bpy.app.handlers.game_post.remove(self.stop)
        if self.offscreen is not None:
            self.offscreen.free()
            self.offscreen = None

    def draw(self):
        '''Render the scene and blit the result to the screen.

        Every ``interval`` ticks, inverts the camera's world matrix to produce
        the view matrix and calls ``offscreen.draw_view3d`` with the cached
        projection matrix and colour management enabled. The latest colour
        texture is blitted to ``pos`` at the configured ``resolution`` using
        ``draw_texture_2d`` every tick.
        '''
        if self.offscreen is None:
            return
        if self._tick % self.interval == 0:
            context = bpy.context
            self.offscreen.draw_view3d(
                self.scene,
                context.view_layer,
                context.space_data,
                context.region,
                self.camera.matrix_world.inverted(),
                self.projection_matrix,
                do_color_management=True
            )
            self._has_image = True
        self._tick += 1

        if self._has_image:
            width, height = self.resolution
            gpu.state.depth_mask_set(False)
            draw_texture_2d(self.offscreen.texture_color, self.pos, width, height)

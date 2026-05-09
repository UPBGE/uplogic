from bge.types import KX_GameObject
from gpu.types import GPUOffScreen
from gpu_extras.presets import draw_texture_2d
import bge
import bpy
import gpu


class RenderToScreen:
    '''Renders a Blender camera into a GPU off-screen buffer and blits it to the screen.

    On construction an off-screen framebuffer of the given ``resolution`` is
    created. Each game tick :meth:`draw` renders the scene from the supplied
    camera's world matrix and projection matrix via ``GPUOffScreen.draw_view3d``
    and then blits the colour texture to screen-space position ``pos``.

    Useful for picture-in-picture views or off-screen cameras.
    '''

    def __init__(self, camera: KX_GameObject, resolution=(1920, 1080), pos=(0, 0)) -> None:
        '''Initialise the RenderToScreen helper.

        Allocates the off-screen buffer, hides Blender overlays, registers
        :meth:`stop` as a ``game_post`` handler, and appends :meth:`draw` to
        the current scene's ``post_draw`` list.

        :param camera: ``KX_GameObject`` whose ``.blenderObject`` is used as
            the render camera.
        :param resolution: ``(width, height)`` tuple for the off-screen
            framebuffer and the on-screen blit size.
        :param pos: ``(x, y)`` screen-space position of the top-left corner
            of the blitted texture.
        '''
        self.offscreen = gpu.types.GPUOffScreen(resolution[0], resolution[1])
        self.resolution = resolution  # [int(resolution[0] * .1), int(resolution[1] * 0.1)]
        self.pos = pos

        context = bpy.context
        context.space_data.overlay.show_overlays = False
        bpy.app.handlers.game_post.append(self.stop)
        bge.logic.getCurrentScene().post_draw.append(self.draw)
        self.scene = bpy.data.scenes.get(camera.scene.name, None)
        if self.scene is None:
            return
        self.camera = camera.blenderObject
        self.shader = GPUOffScreen(int(resolution[0] * .01), int(resolution[1] * 0.01))

    def stop(self, *a):
        '''Restore overlay visibility in the Blender context.

        Registered as a ``game_post`` handler on construction. Sets
        ``space_data.overlay.show_overlays`` back to ``True`` when the game
        session ends.
        '''
        context = bpy.context
        context.space_data.overlay.show_overlays = True

    def draw(self):
        '''Render the scene and blit the result to the screen.

        Inverts the camera's world matrix to produce the view matrix, computes
        the projection matrix via ``calc_matrix_camera``, then calls
        ``offscreen.draw_view3d`` with colour management enabled. The resulting
        colour texture is blitted to ``pos`` at the configured ``resolution``
        using ``draw_texture_2d``.
        '''
        context = bpy.context
        scene = self.scene
        view_matrix = self.camera.matrix_world.inverted()
        width, height = self.resolution
        projection_matrix = self.camera.calc_matrix_camera(
            context.evaluated_depsgraph_get(),
            x=width,
            y=height
        )

        self.offscreen.draw_view3d(
            scene,
            context.view_layer,
            context.space_data,
            context.region,
            view_matrix,
            projection_matrix,
            do_color_management=True
        )

        gpu.state.depth_mask_set(False)
        draw_texture_2d(self.offscreen.texture_color, self.pos, width, height)

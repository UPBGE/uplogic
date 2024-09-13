from bge.types import KX_GameObject
from gpu.types import GPUOffScreen
from gpu_extras.presets import draw_texture_2d
import bge
import bpy
import gpu


class RenderToScreen:

    def __init__(self, camera: KX_GameObject, resolution=(1920, 1080), pos=(0, 0)) -> None:
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
        context = bpy.context
        context.space_data.overlay.show_overlays = True

    def draw(self):
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

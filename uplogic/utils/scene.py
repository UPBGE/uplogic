'''BGE scene utilities for uplogic — coordinate conversion, scene management, and
GPU asset pre-loading.

Provides helpers for replacing the active scene, converting between world, screen, and
pixel coordinate spaces, and two step-by-step GPU loaders (:class:`FileLoader` and
:class:`SceneLoader`) that upload images, materials, and meshes to the GPU one item per
game tick to avoid stalls during level transitions.
'''
from bge import logic
from bge import render
from mathutils import Vector
from uplogic.events import schedule
from uplogic.utils.math import lerp
# from uplogic.console import error
import bpy


def set_scene(scene: str | bpy.types.Scene) -> None:
    '''Replace the currently running scene.

    :param scene: The scene to switch to; accepts either a scene name string or a
        ``bpy.types.Scene`` instance.
    '''
    logic.getCurrentScene().replace(scene)


def get_custom_loop():
    '''Return the custom game loop stored in ``logic.globalDict``.

    :returns: The object stored under key ``'loop'`` in ``logic.globalDict``, or
        ``None`` if no custom loop has been registered.
    '''
    return logic.globalDict.get('loop', None)


def world_to_screen(position: Vector = Vector((0, 0, 0)), inv_y: bool = True, camera=None) -> Vector:
    '''Convert a 3D world position to 2D normalised screen coordinates (0–1 range).

    :param position: The world-space position to project onto the screen.
    :param inv_y: When ``True`` (default), the Y axis of the result is flipped so that
        ``0`` is the top of the screen and ``1`` is the bottom, matching typical UI
        conventions.
    :param camera: The camera to use for projection.  Defaults to the scene's active
        camera when ``None``.
    :returns: A ``Vector`` with the projected X and Y screen coordinates in the 0–1
        range.
    '''
    if camera is None:
        camera = logic.getCurrentScene().active_camera
    pos = Vector(camera.getScreenPosition(position))
    if inv_y:
        pos[1] = 1 - pos[1]
    return pos


def screen_to_world(x: float = None, y: float = None, distance: float = 10, camera=None) -> Vector:
    '''Convert normalised screen coordinates to a 3D world position at a given depth.

    :param x: Normalised X screen coordinate (0–1).  Pass ``None`` to use the current
        mouse X position.
    :param y: Normalised Y screen coordinate (0–1).  Pass ``None`` to use the current
        mouse Y position.
    :param distance: Distance from the camera at which the world point is computed.
    :param camera: The camera to use for un-projection.  Defaults to the scene's active
        camera when ``None``.
    :returns: A ``Vector`` representing the 3D world position.
    '''
    if camera is None:
        camera = logic.getCurrentScene().active_camera
    mouse = logic.mouse
    x = x if x is not None else mouse.position[0]
    y = y if y is not None else mouse.position[1]
    direction = camera.getScreenVect(x, y)
    origin = camera.worldPosition
    aim = direction * -distance
    return origin + (aim)


def screen_to_pixels(pos: Vector):
    '''Scale normalised screen coordinates to pixel coordinates using the current window
    size.

    :param pos: An iterable of at least two elements ``[x, y]`` in the 0–1 normalised
        screen range.
    :returns: A ``Vector`` containing the corresponding pixel X and Y coordinates.
    '''
    return Vector((
        pos[0] * render.getWindowWidth(),
        pos[1] * render.getWindowHeight()
    ))


class FileLoader():
    '''Step-by-step GPU asset loader for the currently open ``.blend`` file.

    Iterates over images, materials, and meshes in sequence, uploading each one to the
    GPU before advancing to the next item.  This spreads the upload cost across multiple
    game ticks so the engine does not stall during a level transition.

    Override :meth:`on_progress` and :meth:`on_finish` to hook into the loading
    lifecycle without subclassing the full class.

    :param start: When ``True``, begin loading immediately upon construction.
    :param lerp_factor: Interpolation factor used by :meth:`scale_loading_bar` to
        smoothly advance the reported progress value between items.
    '''

    def __init__(self, start=False, lerp_factor=0.2):
        self.lerp_factor = lerp_factor
        self._status = 0.0
        self.status = 0.0
        self.item = ''
        self.data = 'textures'
        self.meshes = [mesh for mesh in bpy.data.meshes]
        self.materials = [m for m in bpy.data.materials if not m.is_grease_pencil]
        self.images = [img for img in bpy.data.images]
        self.datasize = len(self.meshes) + len(self.materials) + len(self.images)
        self.finished = False
        if start:
            self.start()

    @property
    def progress(self):
        '''Loading completion fraction in the 0–1 range.

        :returns: Current value of ``_status``.
        '''
        return self._status

    @property
    def value(self):
        '''Alias for :attr:`progress`; loading completion fraction in the 0–1 range.

        :returns: Current value of ``_status``.
        '''
        return self._status

    def start(self):
        '''Begin the loading sequence by creating the temporary helper object and
        scheduling the first :meth:`load_next` call.
        '''
        self.create_object()
        schedule(self.load_next)

    def create_object(self):
        '''Create the invisible temporary Blender object used to force GPU uploads.

        The object is scaled to near-zero so it is effectively invisible, but its
        presence in the scene is enough for the BGE to upload assigned assets to the
        GPU.
        '''
        self.bmesh = bmesh = bpy.data.meshes.new('ContentLoader')
        self.temp_map = temp_mat = bpy.data.materials.new('ContentLoader')
        temp_mat.use_nodes = True
        self.tex_image = tex_image = temp_mat.node_tree.nodes.new('ShaderNodeTexImage')
        temp_mat.node_tree.links.new(tex_image.outputs[0], temp_mat.node_tree.nodes['Principled BSDF'].inputs[0])
        self.bobj = bobj = bpy.data.objects.new('ContentLoader', bmesh)
        bpy.context.collection.objects.link(bobj)
        bmesh.materials.append(temp_mat)

        self.object = logic.getCurrentScene().convertBlenderObject(bobj)
        self.object.worldScale = (0.000001, 0.000001, 0.0000001)

    def scale_loading_bar(self):
        '''Smoothly lerp the reported progress value toward ``_status`` using
        ``lerp_factor``, then schedule the next tick.

        Reschedules itself until ``status`` catches up to ``_status``, at which point
        it hands control back to :meth:`load_next`.
        '''
        self.status = lerp(self.status, self._status, self.lerp_factor)
        schedule(self.load_next if self.status == self._status else self.scale_loading_bar)

    def load_next(self):
        '''Upload the next pending asset to the GPU and advance the progress counter.

        Processes assets in order: images first, then materials, then meshes.  Calls
        :meth:`on_progress` after each item and :meth:`on_finish` when all assets have
        been processed.
        '''
        cam = logic.getCurrentScene().active_camera
        self.object.worldPosition = cam.worldPosition - cam.getAxisVect((0, 0, 1)) * 100
        if self.images:
            self.tex_image.image = self.images.pop()
            self._status += 1 / self.datasize
            self.item = self.tex_image.image.name
            schedule(self.scale_loading_bar)
            self.on_progress(self._status)
            return
        if self.materials:
            mat = self.materials.pop()
            self.object.blenderObject.material_slots[0].material = mat
            self._status += 1 / self.datasize
            self.data = 'shaders'
            self.item = mat.name
            schedule(self.scale_loading_bar)
            self.on_progress(self._status)
            return
        if self.meshes:
            self.bobj.data = self.meshes.pop()
            self._status += 1 / self.datasize
            self.data = 'meshes'
            self.item = self.bobj.data.name
            schedule(self.scale_loading_bar)
            self.on_progress(self._status)
            return
        # NOTE: Remove when crashing!
        self.object.endObject()

        # TODO: 5.1 need to remove all pointers before removing
            # bpy.data.materials.remove(self.temp_map)
            # bpy.data.meshes.remove(self.bmesh)
            # bpy.data.objects.remove(self.bobj)
        self.finished = True
        self.on_finish()

    def on_finish(self):
        '''Override hook called once all assets have been uploaded to the GPU.

        The default implementation does nothing.
        '''
        pass

    def on_progress(self, progress):
        '''Override hook called after each individual asset is uploaded.

        :param progress: Current loading fraction (0–1) after the most recent upload.
        '''
        pass


class SceneLoader():
    '''Step-by-step GPU asset loader scoped to a specific scene in the open
    ``.blend`` file.

    Unlike :class:`FileLoader`, which loads every asset in ``bpy.data``, this loader
    collects only the meshes and materials actually used by objects in *scene*, keeping
    the loading set minimal.  The loading sequence and progress reporting are otherwise
    identical to :class:`FileLoader`.

    :param scene: The scene whose assets should be loaded; accepts either a scene name
        string or a ``bpy.types.Scene`` instance.
    :param start: When ``True`` (default), begin loading immediately upon construction.
    :param lerp_factor: Interpolation factor used by :meth:`scale_loading_bar` to
        smoothly advance the reported progress value between items.
    '''

    def __init__(self, scene: str, start=True, lerp_factor=0.2):
        if isinstance(scene, str):
            scene = bpy.data.scenes.get(scene)
        if not isinstance(scene, bpy.types.Scene):
            from uplogic.console import error
            error(f'SceneLoader: Scene {scene} not found!')
            return

        self.scene = scene
        self._status = 0.0
        self.status = 0.0
        self.lerp_factor = lerp_factor
        self.item = ''
        self.data = 'textures'
        self.meshes = []
        self.materials = []
        self.images = [img for img in bpy.data.images]
        self.finished = False
        self.fetch_data()
        self.datasize = len(self.meshes) + len(self.materials) + len(self.images)
        if start:
            self.start()

    def fetch_data(self):
        '''Populate ``meshes`` and ``materials`` by inspecting every object in the
        target scene.

        Each unique ``bpy.types.Mesh`` data-block and each unique material found in
        any material slot is appended exactly once.
        '''
        for bobj in self.scene.objects:
            if isinstance(bobj.data, bpy.types.Mesh) and bobj.data not in self.meshes:
                self.meshes.append(bobj.data)
            for slot in bobj.material_slots:
                if slot.material not in self.materials:
                    self.materials.append(slot.material)

    def start(self):
        '''Begin the loading sequence by creating the temporary helper object and
        scheduling the first :meth:`load_next` call.
        '''
        self.create_object()
        schedule(self.load_next)

    def create_object(self):
        '''Create the invisible temporary Blender object used to force GPU uploads.

        The object is scaled to near-zero so it is effectively invisible, but its
        presence in the scene is enough for the BGE to upload assigned assets to the
        GPU.
        '''
        self.bmesh = bmesh = bpy.data.meshes.new('ContentLoader')
        self.temp_map = temp_mat = bpy.data.materials.new('ContentLoader')
        temp_mat.use_nodes = True
        self.tex_image = tex_image = temp_mat.node_tree.nodes.new('ShaderNodeTexImage')
        temp_mat.node_tree.links.new(tex_image.outputs[0], temp_mat.node_tree.nodes['Principled BSDF'].inputs[0])
        self.bobj = bobj = bpy.data.objects.new('ContentLoader', bmesh)
        bpy.context.collection.objects.link(bobj)
        bmesh.materials.append(temp_mat)

        self.object = logic.getCurrentScene().convertBlenderObject(bobj)
        self.object.worldScale = (0.000001, 0.000001, 0.0000001)

    def scale_loading_bar(self):
        '''Smoothly lerp the reported progress value toward ``_status`` using
        ``lerp_factor``, then schedule the next tick.

        Reschedules itself until ``status`` catches up to ``_status``, at which point
        it hands control back to :meth:`load_next`.
        '''
        self.status = lerp(self.status, self._status, self.lerp_factor)
        schedule(self.load_next if self.status == self._status else self.scale_loading_bar)

    def load_next(self):
        '''Upload the next pending asset to the GPU and advance the progress counter.

        Processes assets in order: images first, then materials, then meshes.  Calls
        :meth:`on_progress` after each item and :meth:`on_finish` when all assets have
        been processed.
        '''
        cam = logic.getCurrentScene().active_camera
        self.object.worldPosition = cam.worldPosition - cam.getAxisVect((0, 0, 1)) * 100
        if self.images:
            self.tex_image.image = self.images.pop()
            self._status += 1 / self.datasize
            self.item = self.tex_image.image.name
            schedule(self.scale_loading_bar)
            self.on_progress(self._status)
            return
        if self.materials:
            mat = self.materials.pop()
            self.object.blenderObject.material_slots[0].material = mat
            self._status += 1 / self.datasize
            self.data = 'shaders'
            self.item = mat.name
            schedule(self.scale_loading_bar)
            self.on_progress(self._status)
            return
        if self.meshes:
            self.bobj.data = self.meshes.pop()
            self._status += 1 / self.datasize
            self.data = 'meshes'
            self.item = self.bobj.data.name
            schedule(self.scale_loading_bar)
            self.on_progress(self._status)
            return

        # XXX: 5.1 need to remove all pointers before removing
            # self.object.endObject()
            # bpy.data.materials.remove(self.temp_map)
            # bpy.data.objects.remove(self.bobj)
            # bpy.data.meshes.remove(self.bmesh)
        self.finished = True
        self.on_finish()

    def on_progress(self, progress):
        '''Override hook called after each individual asset is uploaded.

        :param progress: Current loading fraction (0–1) after the most recent upload.
        '''
        pass

    def on_finish(self):
        '''Override hook called once all assets have been uploaded to the GPU.

        The default implementation does nothing.
        '''
        pass

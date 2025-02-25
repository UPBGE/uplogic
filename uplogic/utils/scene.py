from bge import logic
from mathutils import Vector
from uplogic.events import schedule
from uplogic.utils.math import lerp
# from uplogic.console import error
import bpy


def set_scene(scene: str | bpy.types.Scene) -> None:
    logic.getCurrentScene().replace(scene)


def get_custom_loop():
    return logic.globalDict.get('loop', None)


def world_to_screen(position: Vector = Vector((0, 0, 0)), inv_y: bool = True) -> Vector:
    pos = Vector(logic.getCurrentScene().active_camera.getScreenPosition(position))
    if inv_y:
        pos[1] = 1 - pos[1]
    return pos


def screen_to_world(x:float = None, y: float = None, distance: float = 10) -> Vector:
    """Get the world coordinates of a point on the screen in a given distance.
    
    :param x: X position on the screen. Leave at `None` to use mouse position.
    :param y: Y position on the screen. Leave at `None` to use mouse position.
    :param distance: The distance from the camera at which to get the position.
    
    :returns: Position as `Vector`
    """

    camera = logic.getCurrentScene().active_camera
    mouse = logic.mouse
    x = x if x is not None else mouse.position[0]
    y = y if y is not None else mouse.position[1]
    direction = camera.getScreenVect(x, y)
    origin = camera.worldPosition
    aim = direction * -distance
    return origin + (aim)


class FileLoader():
    '''Load the content of the currently open .blend file'''

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
        return self._status

    @property
    def value(self):
        return self._status

    def start(self):
        self.create_object()
        schedule(self.load_next)

    def create_object(self):
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
        self.status = lerp(self.status, self._status, self.lerp_factor)
        schedule(self.load_next if self.status == self._status else self.scale_loading_bar)

    def load_next(self):
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
        # XXX: Remove when crashing!
        self.object.endObject()
        bpy.data.materials.remove(self.temp_map)
        bpy.data.meshes.remove(self.bmesh)
        bpy.data.objects.remove(self.bobj)
        self.finished = True
        self.on_finish()

    def on_finish(self):
        pass

    def on_progress(self, progress):
        pass


class SceneLoader():

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
        for bobj in self.scene.objects:
            if isinstance(bobj.data, bpy.types.Mesh) and bobj.data not in self.meshes:
                self.meshes.append(bobj.data)
            for slot in bobj.material_slots:
                if slot.material not in self.materials:
                    self.materials.append(slot.material)

    def start(self):
        self.create_object()
        schedule(self.load_next)

    def create_object(self):
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
        self.status = lerp(self.status, self._status, self.lerp_factor)
        schedule(self.load_next if self.status == self._status else self.scale_loading_bar)

    def load_next(self):
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
        # logic.getCurrentScene().pre_draw.remove(self.load_next)
        self.object.endObject()
        bpy.data.materials.remove(self.temp_map)
        bpy.data.objects.remove(self.bobj)
        bpy.data.meshes.remove(self.bmesh)
        self.finished = True
        self.on_finish()

    def on_progress(self, progress):
        pass

    def on_finish(self):
        pass

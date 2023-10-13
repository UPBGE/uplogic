from bge import logic
import bpy
# from uplogic.events import schedule


def set_scene(scene: str or bpy.types.Scene) -> None:
    logic.getCurrentScene().replace(scene)


class FileLoader():

    def __init__(self, start=True):
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
    
    def start(self):
        self.create_object()
        logic.getCurrentScene().pre_draw.append(self.load_next)

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

    def load_next(self):
        cam = logic.getCurrentScene().active_camera
        self.object.worldPosition = cam.worldPosition - cam.getAxisVect((0, 0, 1)) * 100
        if self.images:
            self.tex_image.image = self.images.pop()
            self.status += 1 / self.datasize
            self.item = self.tex_image.image.name
            return
        if self.materials:
            mat = self.materials.pop()
            self.object.blenderObject.material_slots[0].material = mat
            self.status += 1 / self.datasize
            self.data = 'shaders'
            self.item = mat.name
            return
        if self.meshes:
            self.bobj.data = self.meshes.pop()
            self.status += 1 / self.datasize
            self.data = 'objects'
            self.item = self.bobj.data.name
            return
        logic.getCurrentScene().pre_draw.remove(self.load_next)
        self.object.endObject()
        bpy.data.materials.remove(self.temp_map)
        bpy.data.meshes.remove(self.bmesh)
        bpy.data.objects.remove(self.bobj)
        self.finished = True
        self.on_finish()

    def on_finish(self):
        pass


class SceneLoader():

    def __init__(self, scene: str, start=True):
        if isinstance(scene, str):
            scene = bpy.data.scenes.get(scene)
        if not isinstance(scene, bpy.types.Scene):
            print(f'SceneLoader: Scene {scene} not found!')
            return

        self.scene = scene
        self.status = 0.0
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
        logic.getCurrentScene().pre_draw.append(self.load_next)

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

    def load_next(self):
        cam = logic.getCurrentScene().active_camera
        self.object.worldPosition = cam.worldPosition - cam.getAxisVect((0, 0, 1)) * 100
        if self.images:
            self.tex_image.image = self.images.pop()
            self.status += 1 / self.datasize
            self.item = self.tex_image.image.name
            return
        if self.materials:
            mat = self.materials.pop()
            self.object.blenderObject.material_slots[0].material = mat
            self.status += 1 / self.datasize
            self.data = 'shaders'
            self.item = mat.name
            return
        if self.meshes:
            self.bobj.data = self.meshes.pop()
            self.status += 1 / self.datasize
            self.data = 'objects'
            self.item = self.bobj.data.name
            return
        logic.getCurrentScene().pre_draw.remove(self.load_next)
        self.object.endObject()
        bpy.data.materials.remove(self.temp_map)
        bpy.data.objects.remove(self.bobj)
        bpy.data.meshes.remove(self.bmesh)
        self.finished = True
        self.on_finish()

    def on_finish(self):
        pass

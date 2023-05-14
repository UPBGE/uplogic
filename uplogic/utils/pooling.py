from bge import logic
from uplogic.events import schedule
from bge.types import KX_GameObject as GameObject
import bpy
from mathutils import Vector, Matrix
from .raycasting import raycast, raycast_projectile
from .math import cycle
from .visuals import draw_cube


class Spawn:
    def __init__(self, object: GameObject, pool) -> None:
        schedule(self.destroy, pool._lifetime)
        self._pool = pool
        self._object = None
        self.scene = logic.getCurrentScene()
        if object['spawn'] is None:
            self._object = object
            object.worldPosition = (0, 0, 0)
            object.worldScale = (1, 1, 1)
            object['spawn'] = self
            object.restorePhysics()
            object.worldLinearVelocity = (0, 0, 0)
            object.worldAngularVelocity = (0, 0, 0)
        if pool.spawner:
            self.transform = pool.spawner.worldTransform.copy()
            self.position = pool.spawner.worldPosition.copy()
            self.orientation = pool.spawner.worldOrientation.copy()
        else:
            self.transform = Matrix()
            self.position = Vector((0, 0, 0))
            self.orientation = Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        scene = logic.getCurrentScene()
        if self._update not in scene.pre_draw:
            scene.pre_draw.append(self._update)
        self._visualize = False
        self.start()

    @property
    def transform(self):
        return self._transform
    
    @transform.setter
    def transform(self, pos):
        self._transform = pos
        if self._object:
            self._object.worldTransform = self._transform

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, pos):
        self._position = pos
        if self._object:
            self._object.worldPosition = self._position

    @property
    def orientation(self):
        return self._orientation
    
    @orientation.setter
    def orientation(self, ori):
        self._orientation = ori
        if self._object:
            self._object.worldOrientation = self._orientation

    @property
    def game_object(self):
        return self._object

    @game_object.setter
    def game_object(self, val):
        print("Attribute 'game_object' of 'Spawn' is read-only!")

    def start(self):
        pass

    def _update(self):
        if self._visualize:
            draw_cube(self.position, 1, centered=True)
        self.update()

    def update(self):
        pass

    def destroy(self):
        scene = logic.getCurrentScene()
        if self._update in scene.pre_draw:
            scene.pre_draw.remove(self._update)
        obj = self._object
        if obj and obj['spawn'] is self:
            obj.worldPosition = self._pool._reset_pos
            obj.worldScale = (.001, .001, .001)
            obj['spawn'] = None
            obj.suspendPhysics()
        self.stop()

    def stop(self):
        pass


class SimpleBullet(Spawn):
    speed = 20
    
    def update(self):
        target = self.position + Vector((0, self.speed, 0)) @ self.transform.inverted()
        dat = raycast(self.scene.active_camera, self.position, target)
        
        if not dat.obj:
            self.position = target
        else:
            self.hit()
            self.destroy()
    
    def hit(self):
        pass


class PhysicsBullet(Spawn):
    power = 300
    
    def start(self):
        self.target = Vector((0, 1, 0)) @ self.transform.inverted()
    
    def update(self):
        dat = raycast_projectile(
            self.scene.active_camera,
            self.position,
            self.target,
            power=self.power,
            distance=self.power * .1,
            visualize=self._visualize,
            local=True
        )
        if self.game_object:
            self.game_object.alignAxisToVect(self.target, 1, 1.0)
        
        if not dat.obj:
            self.position = dat.points[-1]
            self.target = dat.points[-1] - dat.points[-2]
        else:
            self.hit()
            self.destroy()
    
    def hit(self):
        pass


class SpawnPool:

    def __init__(
        self,
        object_name: str,
        amount: int = 10,
        lifetime: int = 5,
        spawner = None,
        spawn = Spawn,
        inactive_pos: Vector = Vector((0, 0, -100)),
        visualize: bool = False
    ):
        self.spawn_cls = spawn
        self._spawn_idx = 0
        self.spawner = spawner
        self._amount = amount # clamp(amount, 0, 10)
        self._lifetime = lifetime
        bobj = bpy.data.objects[object_name]
        self._spawn_name = f'Projectile{bobj.data.name}'
        self.scene = logic.getCurrentScene()
        self._reset_pos = inactive_pos
        self.visualize = visualize
        for x in range(self._amount):
            if self.scene.objects.get(f'{self._spawn_name}{x}'):
                continue
            bspawn = bpy.data.objects.new(f'{self._spawn_name}{x}', bobj.data)
            bpy.context.collection.objects.link(bspawn)
            bspawn.location = Vector(inactive_pos)
            bspawn.scale = Vector((.001, .001, .001))
            bspawn.game.physics_type = bobj.game.physics_type
            gobj = self.scene.convertBlenderObject(bspawn)
            gobj['spawn'] = None
            gobj.suspendPhysics()

    def spawn(self):
        spawn_obj = self.scene.objects[f'{self._spawn_name}{self._spawn_idx}']
        spawn = self.spawn_cls(spawn_obj, self)
        spawn._visualize = self.visualize
        self._spawn_idx = cycle(self._spawn_idx + 1, 0, self._amount - 1)
        return spawn


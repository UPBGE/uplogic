from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.pooling import SpawnPool, Spawn, SimpleBullet, PhysicsBullet
from uplogic.events import send, receive


class ULSpawnPool(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.spawn = None
        self.spawner = None
        self.amount = None
        self.object_instance = None
        self.life = None
        self.speed = None
        self.visualize = None
        self.create_on_init = True
        self.spawn_type = 'Simple'
        self._hit_evt = None
        self._spawned = False

        self._pool = None

        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.SPAWNED = ULOutSocket(self, self.get_spawned)
        self.ONHIT = ULOutSocket(self, self.get_hit)
        self.HITOBJECT = ULOutSocket(self, self.get_hit_obj)
        self.HITPOINT = ULOutSocket(self, self.get_hit_point)
        self.HITNORMAL = ULOutSocket(self, self.get_hit_normal)
        self.HITDIR = ULOutSocket(self, self.get_hit_direction)

        class NodeSimple(Spawn):
            pass

        class NodeSimpleBullet(SimpleBullet):
            def hit(self, data):
                send(self._pool, data)

        class NodePhysicsBullet(PhysicsBullet):
            def hit(self, data):
                send(self._pool, data)

        self.spawn_types = {
            'Simple': NodeSimple,
            'SimpleBullet': NodeSimpleBullet,
            'PhysicsBullet': NodePhysicsBullet,
        }

    def get_done(self):
        return self.done

    def get_spawned(self):
        r = self._spawned
        self._spawned = False
        return r

    def get_hit(self):
        return self._hit_evt is not None

    def get_hit_obj(self):
        if self._hit_evt:
            return self._hit_evt.content.obj

    def get_hit_point(self):
        if self._hit_evt:
            return self._hit_evt.content.point

    def get_hit_normal(self):
        if self._hit_evt:
            return self._hit_evt.content.normal

    def get_hit_direction(self):
        if self._hit_evt:
            return self._hit_evt.content.direction

    def setup(self, tree):
        if self.create_on_init:
            self._pool = SpawnPool(
                self.get_input(self.object_instance),
                self.get_input(self.amount),
                self.get_input(self.life),
                self.get_input(self.spawner),
                self.spawn_types[self.get_input(self.spawn_type)],
                visualize=self.get_input(self.visualize)
            )
        self.done = True

    def evaluate(self):
        self.done = False
        spawn = self.get_input(self.spawn)
        self._set_ready()
        if self._pool:
            self._hit_evt = receive(self._pool)
        if spawn and self._pool:
            self._pool.spawn()
            self.spawn_types[self.spawn_type].speed = self.get_input(self.speed)
            self._spawned = True

        if self.get_input(self.condition):
            self._pool = SpawnPool(
                self.get_input(self.object_instance),
                self.get_input(self.amount),
                self.get_input(self.life),
                self.get_input(self.spawner),
                self.spawn_types[self.get_input(self.spawn_type)],
                visualize=self.get_input(self.visualize)
            )
            self.done = True

from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.pooling import SpawnPool, Spawn, SimpleBullet, PhysicsBullet


class ULSpawnPool(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.spawn = None
        self.spawner = None
        self.amount = None
        self.object_instance = None
        self.life = None
        self.visualize = None
        self.create_on_init = True
        self.spawn_type = 'Simple'

        self._pool = None

        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.SPAWNED = None
        self.INSTANCES = None
        self.ONHIT = None
        self.HITOBJECT = None
        self.HITOBJECTS = None

        self.spawn_types = {
            'Simple': Spawn,
            'SimpleBullet': SimpleBullet,
            'PhysicsBullet': PhysicsBullet,
        }

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

    def get_done(self):
        return self.done

    def evaluate(self):
        spawn = self.get_input(self.spawn)
        self._set_ready()
        if spawn and self._pool:
            self._pool.spawn()

        self.done = False
        self.done = True

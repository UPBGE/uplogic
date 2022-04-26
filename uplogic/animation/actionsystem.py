from bge import logic
from uplogic.data import GlobalDB


class ULActionSystem():
    '''TODO: Documentation
    '''
    layers: dict = {}

    def __init__(self, name: str):
        self.actions = []
        scene = logic.getCurrentScene()
        self.listener = scene.active_camera
        self.old_lis_pos = self.listener.worldPosition.copy()
        GlobalDB.retrieve('uplogic.animation').put(name, self)
        scene.pre_draw.append(self.update)

    @classmethod
    def lock_layer(cls, action):
        layers = cls.layers.get(action.game_object, {})
        layers[action.layer] = action
        cls.layers[action.game_object] = layers

    @classmethod
    def free_layer(cls, action):
        layers = cls.layers.get(action.game_object, {})
        layers.pop(action.layer, None)
        cls.layers[action.game_object] = layers

    @classmethod
    def find_free_layer(cls, action):
        layers = cls.layers.get(action.game_object, {})
        action.layer = 0
        while action.layer in layers.keys():
            action.layer += 1

    @classmethod
    def check_layer(cls, action):
        layers = cls.layers.get(action.game_object, {})
        return action.layer in layers.keys()
    
    @classmethod
    def get_layer(cls, game_object, layer=0):
        return cls.layers.get(game_object, {}).get(layer, None)

    def update(self):
        for action in self.actions:
            action.update()

    def add(self, action):
        '''TODO: Documentation
        '''
        self.actions.append(action)
        ULActionSystem.lock_layer(action)

    def remove(self, action):
        '''TODO: Documentation
        '''
        action.stop()
        if action in self.actions:
            self.actions.remove(action)
        ULActionSystem.free_layer(action)

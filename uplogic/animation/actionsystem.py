from bge import logic
from uplogic.data import GlobalDB


class ULActionSystem():
    '''System for managing actions started using `ULAction`. This class is
    usually addressed indirectly through `ULAction` and is not intended for
    manual use.
    '''
    layers: dict = {}

    def __init__(self, name: str):
        self.actions: list = []
        self.scene = scene = logic.getCurrentScene()
        self.listener = scene.active_camera
        self.old_lis_pos = self.listener.worldPosition.copy()
        GlobalDB.retrieve('uplogic.animation').put(name, self)
        scene.pre_draw.append(self.update)
        scene.onRemove.append(self.shutdown)

    @classmethod
    def lock_layer(cls, action):
        """Lock a layer according to a `ULAction`.

        :param `action`: The `ULAction` whose layer will be locked.
        """
        layers = cls.layers.get(action.game_object, {})
        layers[action.layer] = action
        cls.layers[action.game_object] = layers

    @classmethod
    def free_layer(cls, action):
        """Allow for the layer of the given action to be used again.

        :param `action`: The `ULAction` whose layer will be freed.
        """
        layers = cls.layers.get(action.game_object, {})
        layers.pop(action.layer, None)
        cls.layers[action.game_object] = layers

    @classmethod
    def find_free_layer(cls, action):
        """Incrementally find the next free layer for a `ULAction`.

        :param `action`: The `ULAction` for which to find a free layer.
        """
        layers = cls.layers.get(action.game_object, {})
        action.layer = 0
        while action.layer in layers.keys():
            action.layer += 1

    @classmethod
    def check_layer(cls, action):
        """Check if the layer for this `ULAction` is free.

        :param `action`: The `ULAction` whose layer to check.

        :return: `True` if the layer is occupied, `False` if not
        """
        layers = cls.layers.get(action.game_object, {})
        return action.layer in layers.keys()
    
    @classmethod
    def get_layer(cls, game_object, layer=0):
        """Get the `ULAction` of an object on the given layer.

        :param `game_object`: The `KX_GameObject` on which the action is
        playing.
        :param `layer`: The layer on which the action is playing.

        :return: `ULAction` if layer is occupied, else `None`
        """
        return cls.layers.get(game_object, {}).get(layer, None)

    def update(self):
        """This is called each frame.
        """
        for action in self.actions:
            action.update()

    def add(self, action):
        '''Add a `ULAction` to this system.

        :param `action`: `ULAction` to add.
        '''
        self.actions.append(action)
        ULActionSystem.lock_layer(action)

    def remove(self, action):
        '''Remove a `ULAction` from this system.

        :param `action`: `ULAction` which to remove.
        '''
        action.stop()
        if action in self.actions:
            self.actions.remove(action)
        ULActionSystem.free_layer(action)

    def shutdown(self):
        '''Shutdown and remove this action system. This will stop all actions
        playing in this system.'''
        self.scene.pre_draw.remove(self.update)
        for action in self.actions.copy():
            self.remove(action)
        GlobalDB.retrieve('uplogic.animation').remove(self)


def get_action_system(system_name: str = 'default') -> ULActionSystem:
    """Get or create a `ULActionSystem` with the given name. Using more than one
    action system is highly discouraged.

    :param `system_name`: Look for this name.

    :returns: `ULActionSystem`, new system is created if none is found.
    """
    act_systems = GlobalDB.retrieve('uplogic.animation')
    if act_systems.check(system_name):
        return act_systems.get(system_name)
    else:
        return ULActionSystem(system_name)
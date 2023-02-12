from bge import logic
from bge.types import KX_GameObject
from uplogic.data import GlobalDB


class ULActionSystem():
    '''System for managing actions started using `Action`. This class is
    usually addressed indirectly through `Action` and is not intended for
    manual use.
    '''
    layers: dict = {}

    def __init__(self, name: str):
        self.actions: list = []
        self.scene = scene = logic.getCurrentScene()
        GlobalDB.retrieve('uplogic.animation').put(name, self)
        scene.pre_draw.append(self.update)
        scene.onRemove.append(self.shutdown)

    @classmethod
    def lock_layer(cls, action):
        """Lock a layer according to a `Action`.

        :param `action`: The `Action` whose layer will be locked.
        """
        layers = cls.layers.get(action.game_object, {})
        layers[str(action.layer)] = action
        cls.layers[action.game_object] = layers

    @classmethod
    def free_layer(cls, action):
        """Allow for the layer of the given action to be used again.

        :param `action`: The `Action` whose layer will be freed.
        """
        layers = cls.layers.get(action.game_object, {})
        layers.pop(str(action.layer), None)
        cls.layers[action.game_object] = layers

    @classmethod
    def find_free_layer(cls, action):
        """Incrementally find the next free layer for a `Action`.

        :param `action`: The `Action` for which to find a free layer.
        """
        layers = cls.layers.get(action.game_object, {})
        action.layer = 0
        while action.layer in layers.keys():
            action.layer += 1

    @classmethod
    def check_layer(cls, action):
        """Check if the layer for this `Action` is free.

        :param `action`: The `Action` whose layer to check.

        :return: `True` if the layer is occupied, `False` if not
        """
        layers = cls.layers.get(action.game_object, {})
        return str(action.layer) in layers.keys()
    
    @classmethod
    def get_layer(cls, game_object: KX_GameObject, layer: int = 0):
        """Get the `Action` of an object on the given layer.

        :param `game_object`: The `KX_GameObject` on which the action is
        playing.
        :param `layer`: The layer on which the action is playing.

        :return: `Action` if layer is occupied, else `None`
        """
        action = cls.layers.get(game_object, {}).get(str(layer))
        return action

    def update(self):
        """This is called each frame.
        """
        for action in self.actions:
            action.update()

    def add(self, action):
        '''Add a `Action` to this system.

        :param `action`: `Action` to add.
        '''
        self.actions.append(action)
        ULActionSystem.lock_layer(action)

    def remove(self, action):
        '''Remove a `Action` from this system.

        :param `action`: `Action` which to remove.
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

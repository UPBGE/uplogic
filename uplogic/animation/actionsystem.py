from bge import logic
from bge.types import KX_GameObject
from uplogic.data import GlobalDB


class ActionSystem():
    '''Per-scene manager for all active :class:`~uplogic.animation.action.Action`
    instances.

    Handles layer allocation, per-frame updates, and clean shutdown. Usually
    accessed indirectly through :class:`~uplogic.animation.action.Action`
    rather than used directly.
    '''
    layers: dict[KX_GameObject, dict] = {}

    def __init__(self, name: str):
        self.actions: list = []
        self.name = name
        self.scene = scene = logic.getCurrentScene()
        GlobalDB.retrieve('uplogic.animation').put(name, self)
        scene.pre_draw.append(self.update)
        scene.onRemove.append(self.shutdown)

    @classmethod
    def lock_layer(cls, action):
        '''Mark the layer of *action* as occupied so it is not reused.

        :param action: :class:`~uplogic.animation.action.Action` whose layer
            should be locked.
        '''
        layers = cls.layers.get(action.game_object, {})
        layers[str(action.layer)] = action
        cls.layers[action.game_object] = layers

    @classmethod
    def free_layer(cls, action):
        '''Release the layer of *action* so it can be reused.

        :param action: :class:`~uplogic.animation.action.Action` whose layer
            should be freed.
        '''
        layers = cls.layers.get(action.game_object, {})
        layers.pop(str(action.layer), None)
        cls.layers[action.game_object] = layers

    @classmethod
    def find_free_layer(cls, action):
        '''Assign the lowest unused layer index to *action*.

        :param action: :class:`~uplogic.animation.action.Action` that needs a
            free layer; its ``layer`` attribute is updated in-place.
        '''
        layers = cls.layers.get(action.game_object, {})
        action.layer = 0
        while str(action.layer) in layers.keys():
            action.layer += 1

    @classmethod
    def check_layer(cls, action):
        '''Check whether the layer of *action* is already occupied.

        :param action: :class:`~uplogic.animation.action.Action` to check.
        :returns: ``True`` if the layer is occupied, ``False`` if it is free.
        '''
        layers = cls.layers.get(action.game_object, {})
        return str(action.layer) in layers.keys()
    
    @classmethod
    def get_layer(cls, game_object: KX_GameObject, layer: int = 0):
        '''Return the :class:`~uplogic.animation.action.Action` playing on
        *layer* of *game_object*, or ``None`` if the layer is empty.

        :param game_object: The ``KX_GameObject`` to query.
        :param layer: Layer index to look up.
        :returns: :class:`~uplogic.animation.action.Action` or ``None``.
        '''
        action = cls.layers.get(game_object, {}).get(str(layer))
        return action

    @classmethod
    def _get_uppermost_layer(cls, object):
        '''Return the highest-priority layer index whose action has intensity
        ≥ 0.5 and uses ``"blend"`` mode, disabling all layers above it.

        :param object: ``KX_GameObject`` to query.
        :returns: Layer index, or ``None`` if no qualifying action was found.
        '''
        layers = cls.layers.get(object, {})
        found = False
        for action in layers.values().__reversed__():
            if found:
                action.disable()
            elif action.intensity >= .5 and action.blend_mode == 0:
                found = True
                return action.layer

    def update(self):
        '''Per-frame update: forward the update call to every active action.

        Called automatically via the BGE scene pre-draw list.
        '''
        for action in self.actions:
            action.update()

    def add(self, action):
        '''Register *action* with this system and lock its layer.

        :param action: :class:`~uplogic.animation.action.Action` to add.
        '''
        self.actions.append(action)
        self.actions.sort(key=lambda action: action.layer, reverse=True)
        ActionSystem.lock_layer(action)

    def remove(self, action):
        '''Stop *action*, deregister it from this system, and free its layer.

        :param action: :class:`~uplogic.animation.action.Action` to remove.
        '''
        if not action.game_object.invalid:
            action._stop()
        if action in self.actions:
            self.actions.remove(action)
        ActionSystem.free_layer(action)

    def shutdown(self):
        '''Stop all actions, unregister the update hook, and remove this system
        from the global registry.
        '''
        self.scene.pre_draw.remove(self.update)
        for action in self.actions.copy():
            self.remove(action)
        GlobalDB.retrieve('uplogic.animation').remove(self.name)


def get_action_system(system_name: str = 'default') -> ActionSystem:
    '''Get or create an :class:`ActionSystem` with the given name.

    Using more than one action system per scene is strongly discouraged.

    :param system_name: Name of the system to look up.
    :returns: Existing or newly created :class:`ActionSystem`.
    '''
    act_systems = GlobalDB.retrieve('uplogic.animation')
    if act_systems.check(system_name):
        return act_systems.get(system_name)
    else:
        return ActionSystem(system_name)


def get_priority_action(game_object: KX_GameObject, system_name='default'):
    '''Return the layer index of the highest-priority blending action on
    *game_object*, disabling any layers above it.

    :param game_object: ``KX_GameObject`` to query.
    :param system_name: Name of the :class:`ActionSystem` to use.
    :returns: Layer index, or ``None``.
    '''
    return get_action_system(system_name)._get_uppermost_layer(game_object)
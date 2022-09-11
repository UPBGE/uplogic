from uplogic.events import receive, ULEvent
from uplogic.utils.errors import TypeMismatchError
from bge.types import KX_PythonComponent, KX_GameObject


def listener(original_class):
    """`KX_PythonComponent` Class Decorator

    Makes the decorated class listen for events that have the component's
    `object` attribute as ID.
    Executes the component's `on_object` function when an event is detected
    """
    orig_init = original_class.__init__

    def __init__(self, obj):
        orig_init(self)
        obj.scene.post_draw.append(self._detect_object)

    def _detect_object(self):
        evt: ULEvent = receive(self.object)
        if evt:
            self.on_object(evt)

    original_class._detect_object = _detect_object
    original_class.__init__ = __init__
    return original_class


def state_machine(cls):
    """`KX_PythonComponent` Class Decorator.

    Automatically adds a `state` property to the `KX_GameObject` of the Component
    that can be accessed by `KX_PythonComponent.state` as well.
    
    This does not interfere with the built-in `state` attribute of `KX_GameObject`.
    """

    def deco(cls):
        def getState(self, attr_name='state'):
            return self.object[attr_name]

        def setState(self, value, attr_name='state'):
            self.object[attr_name] = value
        
        def set_state(self, state):
            self.state = state

        prop = property(getState, setState)
        setattr(cls, 'state', prop)
        setattr(cls, 'set_state', set_state)
        return cls

    return deco(cls)


def game_props(prop_names):
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.
    
    Automatically adds property handlers for this class to use the `game_object[prop]`
    syntax instead of saving values on the instance itself.

    :param `prop_names`: Names of game properties as a list.
    """
    def deco(cls):
        if not isinstance(prop_names, list):
            raise TypeMismatchError('Expected property names as a list!')
        for game_prop in prop_names:

            def getPropComponent(self, attr_name=game_prop):
                return self.object.get(attr_name)

            def setPropComponent(self, value, attr_name=game_prop):
                self.object[attr_name] = value

            def getPropObject(self, attr_name=game_prop):
                return self.get(attr_name)

            def setPropObject(self, value, attr_name=game_prop):
                self[attr_name] = value

            if issubclass(cls, KX_PythonComponent):
                prop = property(getPropComponent, setPropComponent)
            elif issubclass(cls, KX_GameObject):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, game_prop, prop)
        return cls
    return deco


def bl_attrs(attr_names):
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.
    
    Automatically adds attribute handlers for this class to use the
    `game_object.blenderObject[attribute]` syntax instead of saving values on the
    instance itself.

    :param `attr_names`: Names of game properties as a list.
    """
    def deco(cls):
        if not isinstance(attr_names, list):
            raise TypeMismatchError('Expected attribute names as a list!')
        for attr_name in attr_names:

            def getPropComponent(self, attr_name=attr_name):
                return self.object.blenderObject.get(attr_name)

            def setPropComponent(self, value, attr_name=attr_name):
                self.object.blenderObject[attr_name] = value
                self.object.color = self.object.color

            def getPropObject(self, attr_name=attr_name):
                return self.blenderObject.get(attr_name)

            def setPropObject(self, value, attr_name=attr_name):
                self.blenderObject[attr_name] = value
                self.object.color = self.object.color

            if issubclass(cls, KX_PythonComponent):
                prop = property(getPropComponent, setPropComponent)
            elif issubclass(cls, KX_GameObject):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, attr_name, prop)
        return cls
    return deco


def scene_props(prop_names):
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.
    
    Automatically adds property handlers for this class to use the `game_object.scene[prop]`
    syntax instead of saving values on the instance itself.

    :param `prop_names`: Names of game properties as a list.
    """
    def deco(cls):
        if not isinstance(prop_names, list):
            raise TypeMismatchError('Expected property names as a list!')
        for scene_prop in prop_names:

            def getPropComponent(self, attr_name=scene_prop):
                return self.object.scene.get(attr_name)

            def setPropComponent(self, value, attr_name=scene_prop):
                self.object.scene[attr_name] = value

            def getPropObject(self, attr_name=scene_prop):
                return self.scene.get(attr_name)

            def setPropObject(self, value, attr_name=scene_prop):
                self.scene[attr_name] = value

            if issubclass(cls, KX_PythonComponent):
                prop = property(getPropComponent, setPropComponent)
            elif issubclass(cls, KX_GameObject):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, scene_prop, prop)
        return cls
    return deco

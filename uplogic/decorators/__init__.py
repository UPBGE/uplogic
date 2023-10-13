from uplogic.events import receive, ULEvent
from uplogic.utils.errors import TypeMismatchError
from bge.types import KX_PythonComponent, KX_GameObject
from bge import logic


def listener(original_class: KX_PythonComponent) -> KX_PythonComponent:
    """`KX_PythonComponent` Class Decorator

    Makes the decorated class listen for events that have the component's
    `object` attribute as ID.
    Executes the component's `on_object` function when an event is detected
    """
    if not issubclass(original_class, KX_PythonComponent):
        raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
    orig_init = original_class.__init__

    def __init__(self, obj):
        orig_init(self)
        logic.getCurrentScene().post_draw.append(self._detect_object)

    def _detect_object(self):
        evt: ULEvent = receive(self.object)
        if evt:
            self.on_object(evt)

    original_class._detect_object = _detect_object
    original_class.__init__ = __init__
    return original_class


def state_machine(cls: KX_PythonComponent) -> KX_PythonComponent:
    """`KX_PythonComponent` Class Decorator.

    Automatically adds a `state` property to the `KX_GameObject` of the Component
    that can be accessed by `KX_PythonComponent.state` as well.

    This does not interfere with the built-in `state` attribute of `KX_GameObject`.
    """

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        if not issubclass(cls, KX_PythonComponent):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
        def getState(self, attr_name='state'):
            return self.object.get(attr_name)

        def setState(self, value, attr_name='state'):
            if value != self.state:
                self.on_state(value)
            self.object[attr_name] = value

        def set_state(self, state):
            if state != self.state:
                self.on_state(state)
            self.state = state

        def on_state(self, state):
            pass

        prop = property(getState, setState)
        setattr(cls, 'state', prop)
        setattr(cls, 'set_state', set_state)
        if not hasattr(cls, 'on_state'):
            setattr(cls, 'on_state', on_state)
        return cls

    return deco(cls)


def game_props(*prop_names) -> KX_PythonComponent:
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.

    Automatically adds property handlers for this class to use the `game_object[prop]`
    syntax instead of saving values on the instance itself.

    :param `prop_names`: Names of game properties as a list.
    """

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent or KX_GameObject) -> KX_PythonComponent or KX_GameObject:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent or KX_GameObject subclasses!')
        if not (isinstance(prop_names, list) or isinstance(prop_names, tuple)):
            raise TypeMismatchError('Expected property names as a list or tuple!')
        for game_prop in prop_names:

            def getPropComponent(self, attr_name=game_prop):
                return self.object.get(attr_name)

            def setPropComponent(self, value, attr_name=game_prop):
                getattr(self, f'on_{game_prop}')(value)
                self.object[attr_name] = value

            def getPropObject(self, attr_name=game_prop):
                return self.get(attr_name)

            def setPropObject(self, value, attr_name=game_prop):
                getattr(self, f'on_{game_prop}')(value)
                self[attr_name] = value

            if issubclass(cls, KX_PythonComponent):
                prop = property(getPropComponent, setPropComponent)
            elif issubclass(cls, KX_GameObject):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, game_prop, prop)
            if not hasattr(cls, f'on_{game_prop}'):
                setattr(cls, f'on_{game_prop}', on_attr)
        return cls
    return deco


def instance_props(*prop_names) -> KX_PythonComponent:
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.

    Automatically adds property handlers for this class to use the `game_object.GroupObject[prop]`
    syntax instead of saving values on the instance itself. 

    :param `prop_names`: Names of game properties as a list.
    """

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent or KX_GameObject) -> KX_PythonComponent or KX_GameObject:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent or KX_GameObject subclasses!')
        if not (isinstance(prop_names, list) or isinstance(prop_names, tuple)):
            raise TypeMismatchError('Expected property names as a list or tuple!')
        for game_prop in prop_names:

            def getPropComponent(self, attr_name=game_prop):
                return self.object.groupObject.get(attr_name)

            def setPropComponent(self, value, attr_name=game_prop):
                getattr(self, f'on_{game_prop}')(value)
                self.object.groupObject[attr_name] = value

            def getPropObject(self, attr_name=game_prop):
                return self.groupObject.get(attr_name)

            def setPropObject(self, value, attr_name=game_prop):
                getattr(self, f'on_{game_prop}')(value)
                self.groupObject[attr_name] = value

            if issubclass(cls, KX_PythonComponent):
                prop = property(getPropComponent, setPropComponent)
            elif issubclass(cls, KX_GameObject):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, game_prop, prop)
            if not hasattr(cls, f'on_{game_prop}'):
                setattr(cls, f'on_{game_prop}', on_attr)
        return cls
    return deco


def bl_attrs(*attr_names) -> KX_PythonComponent:
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.

    Automatically adds attribute handlers for this class to use the
    `game_object.blenderObject[attribute]` syntax instead of saving values on the
    instance itself.

    :param `attr_names`: Names of custom attributes as a list.
    """

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent or KX_GameObject) -> KX_PythonComponent or KX_GameObject:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent or KX_GameObject subclasses!')
        if not (isinstance(attr_names, list) or isinstance(attr_names, tuple)):
            raise TypeMismatchError('Expected attribute names as a list or tuple!')
        for attr_name in attr_names:

            def getPropComponent(self, attr_name=attr_name):
                return self.object.blenderObject.get(attr_name)

            def setPropComponent(self, value, attr_name=attr_name):
                getattr(self, f'on_{attr_name}')(value)
                self.object.blenderObject[attr_name] = value
                self.object.color = self.object.color

            def getPropObject(self, attr_name=attr_name):
                return self.blenderObject.get(attr_name)

            def setPropObject(self, value, attr_name=attr_name):
                getattr(self, f'on_{attr_name}')(value)
                self.blenderObject[attr_name] = value
                self.object.color = self.object.color

            if issubclass(cls, KX_PythonComponent):
                prop = property(getPropComponent, setPropComponent)
            elif issubclass(cls, KX_GameObject):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, attr_name, prop)
            if not hasattr(cls, f'on_{attr_name}'):
                setattr(cls, f'on_{attr_name}', on_attr)
        return cls
    return deco


def global_dict(*prop_names):
    """Automatically adds property handlers for this class to use the `bge.logic.globalDict[key]`
    syntax instead of saving values on the instance itself.

    :param `prop_names`: Keys as a list.
    """
    def deco(cls):
        if not (isinstance(prop_names, list) or isinstance(prop_names, tuple)):
            raise TypeMismatchError('Expected property names as a list or tuple!')
        for game_prop in prop_names:

            def getPropComponent(self, attr_name=game_prop):
                return logic.globalDict.get(attr_name)

            def setPropComponent(self, value, attr_name=game_prop):
                logic.globalDict[attr_name] = value

            prop = property(getPropComponent, setPropComponent)

            setattr(cls, game_prop, prop)
        return cls
    return deco


def scene_props(*prop_names):
    """Decorator for `KX_PythonComponent` or `KX_GameObject` classes and subclasses.

    Automatically adds property handlers for this class to use the `game_object.scene[prop]`
    syntax instead of saving values on the instance itself.

    :param `prop_names`: Names of properties as a list.
    """
    def deco(cls: KX_PythonComponent or KX_GameObject) -> KX_PythonComponent or KX_GameObject:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent or KX_GameObject subclasses!')
        if not (isinstance(prop_names, list) or isinstance(prop_names, tuple)):
            raise TypeMismatchError('Expected property names as a list or tuple!')
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

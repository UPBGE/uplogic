'''Class decorators for BGE component and game-object classes.

Each decorator in this module injects Python ``property`` descriptors into a
``KX_PythonComponent`` or ``KX_GameObject`` subclass so that attribute reads
and writes are transparently routed to the underlying BGE data store
(game properties, Blender custom attributes, scene dictionary, etc.) rather
than to plain Python instance attributes.

The setter side of every generated property also calls a corresponding
``on_<name>(value)`` hook method if it exists on the class, giving
subclasses a clean way to react to value changes.

Typical usage::

    from uplogic.decorators import game_property, attribute, scene_property

    @game_property('health', 'speed')
    class Player(KX_PythonComponent):
        def on_health(self, value):
            if value <= 0:
                self.die()
'''

from uplogic.events import receive, Event
from uplogic.console import warning
from uplogic.utils.errors import TypeMismatchError
from bge.types import KX_PythonComponent, KX_GameObject
from uplogic.loop import CustomLoop
from bge import logic
import bpy


class Unset:
    '''Sentinel used to detect missing game-property entries without
    conflicting with ``None`` as a valid stored value.
    '''
    pass


def listener(original_class: KX_PythonComponent) -> KX_PythonComponent:
    '''``KX_PythonComponent`` class decorator that registers the component as
    an event listener.

    After decoration, each instance automatically watches for uplogic
    :class:`~uplogic.events.Event` objects whose ID matches the component's
    ``object`` attribute.  When such an event arrives, the component's
    ``on_object(event)`` method is called.

    :param original_class: The :class:`~bge.types.KX_PythonComponent` subclass
        to decorate.
    :returns: The decorated class with the listener injected.
    :raises TypeMismatchError: When *original_class* is not a
        :class:`~bge.types.KX_PythonComponent` subclass.
    '''
    if not issubclass(original_class, KX_PythonComponent):
        raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
    orig_init = original_class.__init__

    def __init__(self, obj):
        orig_init(self)
        logic.getCurrentScene().post_draw.append(self._detect_object)

    def _detect_object(self):
        evt: Event = receive(self.object)
        if evt:
            self.on_object(evt)

    original_class._detect_object = _detect_object
    original_class.__init__ = __init__
    return original_class


def state_machine(cls: KX_PythonComponent) -> KX_PythonComponent:
    '''``KX_PythonComponent`` class decorator that adds a ``state`` game-property
    accessor and a ``set_state`` helper.

    The injected ``state`` property reads and writes ``self.object["state"]``.
    On every write the ``on_state(new_state)`` hook is called if the value
    actually changed.  This does not conflict with the built-in BGE
    ``KX_GameObject.state`` bitmask attribute.

    :param cls: The :class:`~bge.types.KX_PythonComponent` subclass to decorate.
    :returns: The decorated class.
    :raises TypeMismatchError: When *cls* is not a
        :class:`~bge.types.KX_PythonComponent` subclass.
    '''

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
    '''[DEPRECATED] Use :func:`game_property` instead.

    Injects game-property accessors that delegate to ``game_object[name]``
    (component) or ``self[name]`` (game object).

    :param prop_names: One or more BGE game-property names to wrap.
    :returns: A class decorator that adds the properties.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *prop_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        warning('@game_props decorator is deprecated, use @game_property instead.')
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
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


def game_property(*prop_names) -> KX_PythonComponent:
    '''Decorator that routes named attributes through BGE game properties.

    For each name in *prop_names* a Python ``property`` is added to the
    decorated class.  Reads go to ``self.object[name]``
    (``KX_PythonComponent``) or ``self[name]`` (``KX_GameObject``); writes
    first call ``self.on_<name>(value)`` then update the game property.  A
    no-op ``on_<name>`` stub is added automatically if the class does not
    already define one.

    :param prop_names: One or more BGE game-property names to wrap.
    :returns: A class decorator that adds the properties.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *prop_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
        if not (isinstance(prop_names, list) or isinstance(prop_names, tuple)):
            raise TypeMismatchError('Expected property names as a list or tuple!')
        for game_prop in prop_names:

            def getPropComponent(self, attr_name=game_prop):
                prop = self.object.get(attr_name, Unset)
                if prop is Unset:
                    self.object[attr_name] = 0.0
                return prop

            def setPropComponent(self, value, attr_name=game_prop):
                getattr(self, f'on_{game_prop}')(value)
                self.object[attr_name] = value

            def getPropObject(self, attr_name=game_prop):
                self.get(attr_name)
                if prop is None:
                    self[attr_name] = 0.0
                return prop

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
    '''[DEPRECATED] Use :func:`instance_property` instead.

    Injects property accessors that delegate to ``self.object.groupObject[name]``
    (component) or ``self.groupObject[name]`` (game object).

    :param prop_names: One or more property names to wrap.
    :returns: A class decorator that adds the properties.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *prop_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        warning('@instance_props decorator is deprecated, use @instance_property instead.')
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
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


def instance_property(*prop_names) -> KX_PythonComponent:
    '''Decorator that routes named attributes through the group-instance object.

    For each name in *prop_names* a Python ``property`` is added that reads
    from and writes to ``self.object.groupObject[name]``, falling back to
    ``self.object[name]`` when no group object is present.  Writes call
    ``self.on_<name>(value)`` before updating the property.  A no-op stub is
    added automatically when the class does not already define the hook.

    :param prop_names: One or more property names to wrap.
    :returns: A class decorator that adds the properties.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *prop_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
        if not (isinstance(prop_names, list) or isinstance(prop_names, tuple)):
            raise TypeMismatchError('Expected property names as a list or tuple!')

        for game_prop in prop_names:

            def getPropComponent(self, attr_name=game_prop):
                obj = self.object.groupObject
                if obj:
                    return self.object.groupObject.get(attr_name, self.object.get(attr_name, None))
                return self.object.get(attr_name)

            def setPropComponent(self, value, attr_name=game_prop):
                getattr(self, f'on_{game_prop}')(value)
                obj = self.object.groupObject
                if obj:
                    obj[attr_name] = value
                    return
                self.object[attr_name] = value

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
    '''[DEPRECATED] Use :func:`attribute` instead.

    Injects attribute accessors that delegate to
    ``self.object.blenderObject[name]`` (component) or
    ``self.blenderObject[name]`` (game object).

    :param attr_names: One or more Blender custom-attribute names to wrap.
    :returns: A class decorator that adds the attributes.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *attr_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        warning('@bl_attrs decorator is deprecated, use @attribute instead.')
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
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


def attribute(*attr_names) -> KX_PythonComponent:
    '''Decorator that routes named attributes through Blender custom properties.

    For each name in *attr_names* a Python ``property`` is added that reads
    from and writes to ``self.object.blenderObject[name]`` (component) or
    ``self.blenderObject[name]`` (game object).  Writes call
    ``self.on_<name>(value)`` and then invoke ``update_tag()`` to notify
    Blender of the change.  A no-op stub is added when the class does not
    already define the hook.

    :param attr_names: One or more Blender custom-attribute names to wrap.
    :returns: A class decorator that adds the attributes.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *attr_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
        if not (isinstance(attr_names, list) or isinstance(attr_names, tuple)):
            raise TypeMismatchError('Expected attribute names as a list or tuple!')
        for attr_name in attr_names:

            def getPropComponent(self, attr_name=attr_name):
                return self.object.blenderObject.get(attr_name)

            def setPropComponent(self, value, attr_name=attr_name):
                getattr(self, f'on_{attr_name}')(value)
                self.object.blenderObject[attr_name] = value
                self.object.blenderObject.update_tag()

            def getPropObject(self, attr_name=attr_name):
                return self.blenderObject.get(attr_name)

            def setPropObject(self, value, attr_name=attr_name):
                getattr(self, f'on_{attr_name}')(value)
                self.blenderObject[attr_name] = value
                self.object.blenderObject.update_tag()

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


def scene_attribute(*attr_names) -> KX_PythonComponent:
    '''Decorator that routes named attributes through Blender scene custom properties.

    For each name in *attr_names* a Python ``property`` is added that reads
    from ``bpy.data.scenes[scene.name][name]`` and writes back to it, calling
    ``self.on_<name>(value)`` before each write.  A no-op stub is added when
    the class does not already define the hook.

    :param attr_names: One or more Blender scene-attribute names to wrap.
    :returns: A class decorator that adds the attributes.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *attr_names* is not a list or tuple.
    '''

    def on_attr(self, val):
        pass

    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent subclasses!')
        if not (isinstance(attr_names, list) or isinstance(attr_names, tuple)):
            raise TypeMismatchError('Expected attribute names as a list or tuple!')
        for attr_name in attr_names:

            def getPropComponent(self, attr_name=attr_name):
                return bpy.data.scenes[self.object.scene.name].get(attr_name)

            def setPropComponent(self, value, attr_name=attr_name):
                getattr(self, f'on_{attr_name}')(value)
                bpy.data.scenes[self.object.scene.name] = value
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
    '''Decorator that routes named attributes through ``bge.logic.globalDict``.

    For each name in *prop_names* a Python ``property`` is added that reads
    from and writes to ``logic.globalDict[name]``.  Unlike the other
    decorators in this module, no ``on_<name>`` hook is generated and there
    is no class-type restriction.

    :param prop_names: One or more ``globalDict`` keys to expose as properties.
    :returns: A class decorator that adds the properties.
    :raises TypeMismatchError: When *prop_names* is not a list or tuple.
    '''
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
    '''[DEPRECATED] Use :func:`scene_property` instead.

    Injects property accessors that delegate to ``self.object.scene[name]``
    (component) or ``self.scene[name]`` (game object / :class:`CustomLoop`).

    :param prop_names: One or more scene-property names to wrap.
    :returns: A class decorator that adds the properties.
    :raises TypeMismatchError: When applied to an incompatible class or when
        *prop_names* is not a list or tuple.
    '''
    def deco(cls: KX_PythonComponent) -> KX_PythonComponent:
        warning('@scene_props decorator is deprecated, use @scene_property instead.')
        if not (issubclass(cls, KX_PythonComponent) or issubclass(cls, KX_GameObject) or issubclass(cls, CustomLoop)):
            raise TypeMismatchError('Decorator only viable for KX_PythonComponent, KX_GameObject or CustomLoop subclasses!')
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
            elif issubclass(cls, KX_GameObject) or issubclass(cls, CustomLoop):
                prop = property(getPropObject, setPropObject)
            else:
                return

            setattr(cls, scene_prop, prop)
        return cls
    return deco


def scene_property(*prop_names):
    '''Decorator that routes named attributes through the current BGE scene dictionary.

    For each name in *prop_names* a Python ``property`` is added that reads
    from and writes to ``logic.getCurrentScene()[name]``.  There is no
    class-type restriction and no ``on_<name>`` hook is generated.

    :param prop_names: One or more scene-dictionary keys to expose as properties.
    :returns: A class decorator that adds the properties.
    '''
    def deco(cls):
        for scene_prop in prop_names:

            def getProp(self, attr_name=scene_prop):
                return logic.getCurrentScene().get(attr_name)

            def setProp(self, value, attr_name=scene_prop):
                logic.getCurrentScene()[attr_name] = value

            prop = property(getProp, setProp)

            setattr(cls, scene_prop, prop)
        return cls
    return deco

'''BGE collection utilities providing object-group management and state save/restore.
'''
from bge import logic
from bge import constraints
from bpy.types import Collection as BColl
import bpy, bge
from mathutils import Vector, Euler
from uplogic import events


def assign(game_object: bge.types.KX_GameObject, collection: BColl, exclusive=True):
    '''Link a game object's Blender object into a specified collection.

    :param game_object: The ``KX_GameObject`` whose underlying Blender object will be
        linked into *collection*.
    :param collection: Target collection; accepts either a ``bpy.types.Collection``
        instance or a collection name string.
    :param exclusive: When ``True`` (default), the object is first removed from all its
        current collections before being linked into *collection*.
    '''
    if exclusive:
        for coll in game_object.blenderObject.users_collection:
            coll.objects.unlink(game_object.blenderObject)
    if isinstance(collection, str):
        collection = bpy.data.collections.get(collection)
    collection.objects.link(game_object.blenderObject)
    game_object.blenderObject.update_tag()


def spawn(name, position=None, rotation=None, scale=None, transform=None, parent_collection=None):
    inst: bpy.types.Object = bpy.data.objects.new(name=name, object_data=None)
    if position is not None:
        inst.location = position
    if rotation is not None:
        inst.rotation_euler = rotation
    if scale is not None:
        inst.scale = scale
    if transform is not None:
        inst.matrix_world = transform
    inst.instance_type = 'COLLECTION'
    inst.instance_collection = bpy.data.collections.get(name, None)
    if inst.instance_collection is None:
        bpy.data.objects.remove(inst)
        return
    parent_collection = parent_collection if parent_collection is not None else bpy.context.collection
    parent_collection.objects.link(inst)
    game_obj = logic.getCurrentScene().convertBlenderObject(inst)
    inst.instance_collection = None
    inst.instance_type = 'NONE'
    parent_collection.objects.unlink(inst)
    return game_obj


class Collection:
    '''Wraps a ``bpy.types.Collection`` to provide group-level visibility, physics
    toggling, and state save/restore for all objects in the collection.

    The initial state of every object is snapshotted during construction via
    :meth:`save`, so calling :meth:`load` at any later point restores the scene to
    the condition it was in when the wrapper was created.

    :param collection: The collection to wrap; accepts either a ``BColl`` instance or
        a collection name string.
    '''

    @property
    def game_objects(self):
        '''All ``KX_GameObject`` instances for the collection's direct members.

        :returns: List of ``KX_GameObject`` corresponding to ``collection.objects``.
        '''
        scene = logic.getCurrentScene()
        return [scene.getGameObjectFromObject(bobj) for bobj in self.collection.objects]

    @property
    def all_game_objects(self):
        '''All ``KX_GameObject`` instances in the collection, including nested children
        and group members.

        :returns: List of ``KX_GameObject`` corresponding to ``collection.all_objects``,
            extended with the members of any group instances found in that set.
        '''
        scene = logic.getCurrentScene()
        objs = [scene.getGameObjectFromObject(bobj) for bobj in self.collection.all_objects]
        for o in objs:
            if o.groupMembers is not None and o.groupObject is None:
                objs.extend(o.groupMembers)
        return objs

    @property
    def objects(self):
        '''Raw ``bpy.types.Object`` list of direct collection members (no recursion).

        :returns: ``bpy.types.Collection.objects``
        '''
        return self.collection.objects

    @property
    def all_objects(self):
        '''Raw ``bpy.types.Object`` list including all nested and descendant objects.

        :returns: ``bpy.types.Collection.all_objects``
        '''
        return self.collection.all_objects

    def __init__(self, collection: BColl) -> None:
        if isinstance(collection, str):
            collection = bpy.data.collections.get(collection)
        self.collection = collection
        if collection is None:
            return
        self._collection_state = {
            'objects': []
        }
        self.save()

    def set_frozen(self, state):
        '''Suspend or restore physics and dynamics for every game object in the
        collection.

        Group instances (objects whose ``groupMembers`` is not ``None`` and whose
        ``groupObject`` is ``None``) are skipped.

        :param state: ``True`` to suspend physics and dynamics; ``False`` to restore
            them.
        '''
        for obj in self.all_game_objects:
            if not (obj.groupMembers is not None and obj.groupObject is None):
                obj.suspendPhysics() if state else obj.restorePhysics()
                obj.suspendDynamics() if state else obj.restoreDynamics()

    def set_visible(self, state=True, physics=True):
        '''Show or hide all objects in the collection, optionally toggling physics.

        Group instances are always force-hidden regardless of *state*.

        :param state: ``True`` to make objects visible; ``False`` to hide them.
        :param physics: When ``True``, physics and dynamics are also restored on show
            or suspended on hide alongside the visibility change.
        '''
        for obj in self.all_game_objects:
            if obj.groupMembers is not None and obj.groupObject is None:
                # Is groupInstance
                obj.setVisible(False, True)
            else:
                obj.setVisible(state, False)
                if physics:
                    obj.restorePhysics() if state else obj.suspendPhysics()
                    obj.restoreDynamics() if state else obj.suspendDynamics()
        bpy.context.scene.update_tag()

    def enable(self):
        '''Show all objects in the collection.

        Convenience wrapper for ``set_visible(True)``.
        '''
        self.set_visible(True)

    def disable(self):
        '''Hide all objects in the collection.

        Convenience wrapper for ``set_visible(False)``.
        '''
        self.set_visible(False)

    def get_game_vec(self, data):
        '''Convert a mapping with ``x``/``y``/``z`` keys to an ``Euler``.

        :param data: Dictionary with float values keyed by ``'x'``, ``'y'``, and
            ``'z'``.
        :returns: ``mathutils.Euler`` built from the three components.
        '''
        return Euler((data['x'], data['y'], data['z']))

    def load(self):
        '''Restore all snapshotted state from ``_collection_state`` back to the
        corresponding game objects.

        World and local transforms are applied to every recorded object.
        Additionally:

        - Rigid-body objects have their ``worldLinearVelocity`` and
          ``worldAngularVelocity`` restored.
        - Character-physics objects have their ``walkDirection`` restored.
        - Game properties that were recorded during :meth:`save` are written back to
          each object.
        '''
        scene = logic.getCurrentScene()
        for obj in self.all_objects:
            data = self._collection_state['objects'].get(obj.name, None)
            if data is None:
                continue
            game_obj = scene.getGameObjectFromObject(obj)

            lPos = self.get_game_vec(data['data']['localPosition'])
            lOri = self.get_game_vec(data['data']['localOrientation'])
            lSca = self.get_game_vec(data['data']['localScale'])

            wPos = self.get_game_vec(data['data']['worldPosition'])
            wOri = self.get_game_vec(data['data']['worldOrientation'])
            wSca = self.get_game_vec(data['data']['worldScale'])

            game_obj.worldPosition = wPos
            game_obj.worldOrientation = wOri.to_matrix()
            game_obj.worldScale = wSca

            if game_obj.parent:
                game_obj.localPosition = lPos
                game_obj.localOrientation = lOri.to_matrix()
                game_obj.localScale = lSca

            if data['type'] == 'rigid_body':
                linVel = self.get_game_vec(
                    data['data']['worldLinearVelocity']
                )
                angVel = self.get_game_vec(
                    data['data']['worldAngularVelocity']
                )
                game_obj.worldLinearVelocity = linVel
                game_obj.worldAngularVelocity = angVel

            if data['type'] == 'light':
                energy = data['data']['energy']
                game_obj.energy = energy

            if data['type'] == 'character':
                wDir = self.get_game_vec(data['data']['walkDirection'])
                (
                    constraints
                    .getCharacter(game_obj)
                    .walkDirection
                ) = wDir

            for prop in data['data']['props']:
                game_obj[prop['name']] = prop['value']

    def save(self, properties=True):
        '''Snapshot the current transform, velocity, physics type, and optionally game
        properties of every game object into ``_collection_state``.

        The physics type of each object determines which additional fields are stored:

        - ``RIGID_BODY``: world/local transform plus world linear and angular velocity.
        - Character (``constraints.getCharacter`` returns a controller): world/local
          transform plus ``walkDirection``.
        - All other types (static): world/local transform only.

        Properties whose names start with ``NL__`` or whose values are ``Vector``
        instances are excluded.  The default camera object (``__default__cam__``) is
        skipped entirely.

        :param properties: When ``True`` (default), game properties are included in the
            snapshot.
        '''
        self._collection_state = {
            'objects': {}
        }
        objs = self._collection_state['objects']

        for obj in self.all_game_objects:
            if obj.name == '__default__cam__':
                continue
            props = obj.getPropertyNames()
            prop_list = []
            cha = constraints.getCharacter(obj)
            if properties:
                for prop in props:
                    if prop.startswith('NL__'):
                        continue
                    if isinstance(obj[prop], Vector):
                        continue
                    prop_set = {}
                    prop_set['name'] = prop
                    prop_set['value'] = obj[prop]
                    prop_list.append(prop_set)

            locloc = obj.localPosition
            locrot = obj.localOrientation.to_euler()
            locsca = obj.localScale

            loc = obj.worldPosition
            rot = obj.worldOrientation.to_euler()
            sca = obj.worldScale

            if obj.blenderObject.game.physics_type == 'RIGID_BODY':
                lin_vel = obj.worldLinearVelocity
                ang_vel = obj.worldAngularVelocity
                loclin_vel = obj.localLinearVelocity
                locang_vel = obj.localAngularVelocity

                objs[obj.blenderObject.name] = {
                        'name': obj.name,
                        'type': 'rigid_body',
                        'data': {
                            'localPosition': {
                                'x': locloc.x,
                                'y': locloc.y,
                                'z': locloc.z
                            },
                            'localOrientation': {
                                'x': locrot.x,
                                'y': locrot.y,
                                'z': locrot.z
                            },
                            'localScale': {
                                'x': locsca.x,
                                'y': locsca.y,
                                'z': locsca.z
                            },
                            'worldPosition': {
                                'x': loc.x,
                                'y': loc.y,
                                'z': loc.z
                            },
                            'worldOrientation': {
                                'x': rot.x,
                                'y': rot.y,
                                'z': rot.z
                            },
                            'worldLinearVelocity': {
                                'x': lin_vel.x,
                                'y': lin_vel.y,
                                'z': lin_vel.z
                            },
                            'worldAngularVelocity': {
                                'x': ang_vel.x,
                                'y': ang_vel.y,
                                'z': ang_vel.z
                            },
                            'localLinearVelocity': {
                                'x': loclin_vel.x,
                                'y': loclin_vel.y,
                                'z': loclin_vel.z
                            },
                            'localAngularVelocity': {
                                'x': locang_vel.x,
                                'y': locang_vel.y,
                                'z': locang_vel.z
                            },
                            'worldScale': {'x': sca.x, 'y': sca.y, 'z': sca.z},
                            'props': prop_list
                        }
                    }
            elif cha:
                wDir = cha.walkDirection

                objs[obj.blenderObject.name] = {
                        'name': obj.name,
                        'type': 'character',
                        'data': {
                            'localPosition': {
                                'x': locloc.x,
                                'y': locloc.y,
                                'z': locloc.z
                            },
                            'localOrientation': {
                                'x': locrot.x,
                                'y': locrot.y,
                                'z': locrot.z
                            },
                            'localScale': {
                                'x': locsca.x,
                                'y': locsca.y,
                                'z': locsca.z
                            },
                            'worldPosition': {
                                'x': loc.x,
                                'y': loc.y,
                                'z': loc.z
                            },
                            'worldOrientation': {
                                'x': rot.x,
                                'y': rot.y,
                                'z': rot.z
                            },
                            'worldScale': {'x': sca.x, 'y': sca.y, 'z': sca.z},
                            'walkDirection': {
                                'x': wDir.x,
                                'y': wDir.y,
                                'z': wDir.z
                            },
                            'props': prop_list
                        }
                    }
            else:
                objs[obj.blenderObject.name] = {
                        'name': obj.name,
                        'type': 'static',
                        'data': {
                            'localPosition': {
                                'x': locloc.x,
                                'y': locloc.y,
                                'z': locloc.z
                            },
                            'localOrientation': {
                                'x': locrot.x,
                                'y': locrot.y,
                                'z': locrot.z
                            },
                            'localScale': {
                                'x': locsca.x,
                                'y': locsca.y,
                                'z': locsca.z
                            },
                            'worldPosition': {
                                'x': loc.x,
                                'y': loc.y,
                                'z': loc.z
                            },
                            'worldOrientation': {
                                'x': rot.x,
                                'y': rot.y,
                                'z': rot.z
                            },
                            'worldScale': {'x': sca.x, 'y': sca.y, 'z': sca.z},
                            'props': prop_list
                        }
                    }
            self._collection_state['objects'] = objs

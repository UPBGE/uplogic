from bge import logic
from bge import constraints
from bpy.types import Collection
import bpy
from mathutils import Vector, Euler


class Collection:

    @property
    def game_objects(self):
        scene = logic.getCurrentScene()
        return [scene.getGameObjectFromObject(bobj) for bobj in self.collection.objects]

    @property
    def objects(self):
        return self.collection.objects

    def __init__(self, collection: Collection) -> None:
        if isinstance(collection, str):
            collection = bpy.data.collections.get(collection)
        self.collection = collection
        if collection is None:
            return
        self._collection_state = {
            'objects': []
        }
        self.save()

    def set_visible(self, state=True):
        for obj in self.game_objects:
            obj.setVisible(state, True)
            obj.restorePhysics() if state else obj.suspendPhysics()
            obj.restoreDynamics() if state else obj.suspendDynamics()

    def enable(self):
        self.set_visible(True)

    def disable(self):
        self.set_visible(False)

    def get_game_vec(self, data):
        return Euler((data['x'], data['y'], data['z']))

    def load(self):
        scene = logic.getCurrentScene()
        for obj in self.objects:
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
        self._collection_state = {
            'objects': {}
        }
        objs = self._collection_state['objects']

        for obj in self.game_objects:
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

            if obj.mass:
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
            if cha:
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
            

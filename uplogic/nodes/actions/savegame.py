from bge import constraints
from bge import logic
from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.nodes.logictree import ULLogicTree
import json
import os


class ULSaveGame(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.slot = None
        self.path = ''
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def get_custom_path(self, path):
        if not path.endswith('/') and not path.endswith('json'):
            path = path + '/'
        return path

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        slot = self.get_input(self.slot)
        cust_path = self.get_custom_path(self.path)

        path = (
            logic.expandPath('//Saves/') if self.path == ''
            else cust_path
        )
        os.makedirs(path, exist_ok=True)

        scene = logic.getCurrentScene()
        data = {
            'objects': []
        }

        objs = data['objects']

        for obj in scene.objects:
            if obj.name == '__default__cam__':
                continue
            props = obj.getPropertyNames()
            prop_list = []
            cha = constraints.getCharacter(obj)
            for prop in props:
                if prop != 'NodeTree':
                    if isinstance(obj[prop], ULLogicTree):
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

                objs.append(
                    {
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
                            'worldScale': {'x': sca.x, 'y': sca.y, 'z': sca.z},
                            'props': prop_list
                        }
                    }
                )
            if cha:
                wDir = cha.walkDirection

                objs.append(
                    {
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
                )
            else:
                objs.append(
                    {
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
                )
            data['globalDict'] = logic.globalDict

        with open(path + 'save' + str(slot) + ".json", "w") as file:
            json.dump(data, file, indent=2)

        self.done = True

from mathutils import Vector
from mathutils import Matrix
from bge.types import KX_GameObject


class Vec2(list):

    def __init__(self, vec2: Vector):
        self.append(vec2.x)
        self.append(vec2.y)


class Vec3(list):

    def __init__(self, vec3: Vector):
        self.append(vec3.x)
        self.append(vec3.y)
        self.append(vec3.z)


class Vec4(list):

    def __init__(self, vec4: Vector):
        self.append(vec4.x)
        self.append(vec4.y)
        self.append(vec4.z)
        self.append(vec4.w)


class Mat3(list):

    def __init__(self, mat3: Matrix):
        self.append([0, 0, 0])
        self.append([0, 0, 0])
        self.append([0, 0, 0])

        self[0][0] = mat3[0][0]
        self[0][1] = mat3[0][1]
        self[0][2] = mat3[0][2]
        self[1][0] = mat3[1][0]
        self[1][1] = mat3[1][1]
        self[1][2] = mat3[1][2]
        self[2][0] = mat3[2][0]
        self[2][1] = mat3[2][1]
        self[2][2] = mat3[2][2]


class Mat4(list):

    def __init__(self, mat4: Matrix):
        self.append([0, 0, 0, 0])
        self.append([0, 0, 0, 0])
        self.append([0, 0, 0, 0])
        self.append([0, 0, 0, 0])

        self[0][0] = mat4[0][0]
        self[0][1] = mat4[0][1]
        self[0][2] = mat4[0][2]
        self[0][3] = mat4[0][3]

        self[1][0] = mat4[1][0]
        self[1][1] = mat4[1][1]
        self[1][2] = mat4[1][2]
        self[1][3] = mat4[1][3]

        self[2][0] = mat4[2][0]
        self[2][1] = mat4[2][1]
        self[2][2] = mat4[2][2]
        self[2][3] = mat4[2][3]

        self[3][0] = mat4[3][0]
        self[3][1] = mat4[3][1]
        self[3][2] = mat4[3][2]
        self[3][3] = mat4[3][3]


class GameObj(dict):

    def __init__(self, game_obj: KX_GameObject):
        self['name'] = game_obj.name
        self['data_id'] = game_obj.blenderObject.data.name

        self['worldPosition'] = Vec3(game_obj.worldPosition)
        self['worldOrientation'] = Mat3(game_obj.worldOrientation)
        self['worldScale'] = Vec3(game_obj.worldScale)
        # self['worldLinearVelocity'] = Vec3(game_obj.worldLinearVelocity)
        # self['worldAngularVelocity'] = Vec3(game_obj.worldAngularVelocity)
        self['worldTransform'] = Mat4(game_obj.worldTransform)

        self['localPosition'] = Vec3(game_obj.localPosition)
        self['localOrientation'] = Mat3(game_obj.localOrientation)
        self['localScale'] = Vec3(game_obj.localScale)
        # self['localLinearVelocity'] = Vec3(game_obj.localLinearVelocity)
        # self['localAngularVelocity'] = Vec3(game_obj.localAngularVelocity)
        self['localTransform'] = Mat4(game_obj.localTransform)
        props = self['properties'] = {}
        for prop in game_obj.getPropertyNames():
            if game_obj[prop].__class__ in [int, float, bool, str]:
                props[prop] = game_obj[prop]
        
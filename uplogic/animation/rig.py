from bge.types import BL_ArmatureChannel, BL_ArmatureObject
from bge.logic import ROT_MODE_XYZ
from uplogic.utils.objects import GameObject
from mathutils import Vector, Quaternion, Matrix


class RigBone():

    def __init__(self, bone: BL_ArmatureChannel, armature: BL_ArmatureObject) -> None:
        self.bone = bone
        self.armature = armature
        self._armature = self.armature.blenderObject.data
        # self.bone.rotation_mode = rotation_mode

    @property
    def name(self):
        return self.bone.name

    @name.setter
    def name(self, val):
        self._armature.blenderObject.bones[self.bone.name].name = val

    @property
    def constraints(self):
        return self.armature.blenderObject.pose.bones[self.bone.name].constraints

    @property
    def head(self):
        return self._armature.bones[self.bone.name].head

    @head.setter
    def head(self, value):
        self._armature.bones[self.bone.name].head = value

    @property
    def head_local(self):
        return self._armature.bones[self.bone.name].head_local

    @head_local.setter
    def head_local(self, value):
        self._armature.bones[self.bone.name].head_local = value

    @property
    def tail(self):
        return self._armature.bones[self.bone.name].tail

    @tail.setter
    def tail(self, value):
        self._armature.bones[self.bone.name].tail = value

    @property
    def tail_local(self):
        return self._armature.bones[self.bone.name].tail_local

    @tail_local.setter
    def tail_local(self, value):
        self._armature.bones[self.bone.name].tail_local = value

    @property
    def inherit_rotation(self):
        return self._armature.bones[self.bone.name].use_inherit_rotation

    @inherit_rotation.setter
    def inherit_rotation(self, value):
        self._armature.bones[self.bone.name].use_inherit_rotation = value

    @property
    def inherit_scale(self):
        return self._armature.bones[self.bone.name].use_inherit_scale

    @inherit_scale.setter
    def inherit_scale(self, value):
        self._armature.bones[self.bone.name].use_inherit_scale = value

    @property
    def connected(self):
        return self._armature.bones[self.bone.name].use_connect

    @connected.setter
    def connected(self, value):
        self._armature.bones[self.bone.name].use_connect = value

    @property
    def deform(self):
        return self._armature.bones[self.bone.name].use_deform

    @deform.setter
    def deform(self, value):
        self._armature.bones[self.bone.name].use_deform = value

    @property
    def local_location(self):
        return self._armature.bones[self.bone.name].use_local_location

    @local_location.setter
    def local_location(self, value):
        self._armature.bones[self.bone.name].use_local_location = value

    @property
    def relative_parent(self):
        return self._armature.bones[self.bone.name].use_relative_parent

    @relative_parent.setter
    def relative_parent(self, value):
        self._armature.bones[self.bone.name].use_relative_parent = value

    @property
    def scale_easing(self):
        return self._armature.bones[self.bone.name].use_scale_easing

    @scale_easing.setter
    def scale_easing(self, value):
        self._armature.bones[self.bone.name].use_scale_easing = value

    @property
    def pose_matrix_cleaned(self):
        offset_m4 = (Matrix.Translation(self.bone.location) @ Quaternion(self.bone.rotation_quaternion).to_matrix().to_4x4())
        return self.bone.pose_matrix @ offset_m4.inverted()

    @property
    def localPosition(self):
        return self.bone.location @ self.bone.channel_matrix.inverted()

    @localPosition.setter
    def localPosition(self, val):
        self.bone.location = self.pose_matrix_cleaned.inverted() @ self.armature.worldTransform.inverted() @ (Vector(val) + self.armature.worldPosition)
        self.armature.blenderObject.update_tag()

    @property
    def worldPosition(self):
        return self.bone.location @ self.bone.pose_matrix.inverted()

    @worldPosition.setter
    def worldPosition(self, val):
        self.bone.location = self.pose_matrix_cleaned.inverted() @ self.armature.worldTransform.inverted() @ Vector(val)
        self.armature.blenderObject.update_tag()

    @property
    def worldOrientation(self):
        return self.bone.location @ self.bone.pose_matrix.inverted()

    @worldOrientation.setter
    def worldOrientation(self, val: Matrix):
        _mode = self.bone.rotation_mode
        self.bone.rotation_mode = ROT_MODE_XYZ
        self.bone.rotation_euler = Vector(val.to_euler())
        self.armature.blenderObject.update_tag()
        self.bone.rotation_mode = _mode


class RigBones(dict):
    pass


class Rig(GameObject):

    def __init__(
        self,
        armature
    ) -> None:
        self.game_object: BL_ArmatureObject = armature
        self.bones: RigBones[str, RigBone] = RigBones()
        for bone in self.game_object.channels:
            self.bones[bone.name] = RigBone(bone, armature)

    def set_bone_pos(self, bone: str, pos: Vector):
        self.bones[bone].worldPosition = pos

    def set_bone_rot(self, bone: str, rot: Quaternion):
        bone = self.game_object.channels[bone]
        bone.rotation_quaternion = bone.pose_matrix.inverted() @ Quaternion(rot)

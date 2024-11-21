from bge.types import BL_ArmatureChannel, BL_ArmatureObject
from bge.logic import ROT_MODE_XYZ
from uplogic.utils.objects import GameObject
from mathutils import Vector, Quaternion, Matrix
from uplogic.utils.visualize import draw_line


class RigBone():

    def __init__(self, bone: BL_ArmatureChannel, armature: BL_ArmatureObject) -> None:
        self.world_space = False
        self.bone = bone
        self.armature = armature
        self._armature_data = self.armature.blenderObject.data
        self._pose = self.armature.blenderObject.pose

    @property
    def attr_transform(self):
        return self.armature.worldTransform if self.world_space else Matrix()

    @property
    def armature(self):
        return self._armature

    @armature.setter
    def armature(self, val):
        self._armature_data = val.blenderObject.data
        self._armature = val

    @property
    def name(self):
        return self.bone.name

    @name.setter
    def name(self, val):
        self._armature_data.blenderObject.bones[self.bone.name].name = val

    @property
    def constraints(self):
        return self._pose.bones[self.bone.name].constraints

    @property
    def location(self):
        return self._pose.bones[self.bone.name].location

    @location.setter
    def location(self, val):
        self._pose.bones[self.bone.name].location = val

    @property
    def head(self) -> Vector:
        return self.attr_transform @ self._armature_data.bones[self.bone.name].head

    @head.setter
    def head(self, value):
        self._armature_data.bones[self.bone.name].head = value

    @property
    def head_local(self) -> Vector:
        return self._armature_data.bones[self.bone.name].head_local

    @head_local.setter
    def head_local(self, value):
        self._armature_data.bones[self.bone.name].head_local = value

    @property
    def head_pose(self) -> Vector:
        return self.attr_transform @ self._pose.bones[self.bone.name].head

    @head_pose.setter
    def head_pose(self, val):
        self._pose.bones[self.bone.name].head = val

    @property
    def tail(self) -> Vector:
        return self.attr_transform @ self._armature_data.bones[self.bone.name].tail

    @tail.setter
    def tail(self, value):
        self._armature_data.bones[self.bone.name].tail = value

    @property
    def tail_local(self) -> Vector:
        return self._armature_data.bones[self.bone.name].tail_local

    @tail_local.setter
    def tail_local(self, value):
        self._armature_data.bones[self.bone.name].tail_local = value

    @property
    def tail_pose(self) -> Vector:
        return self.attr_transform @ self._pose.bones[self.bone.name].tail

    @tail_pose.setter
    def tail_pose(self, val):
        self._pose.bones[self.bone.name].tail = val

    @property
    def center(self) -> Vector:
        return self.head.lerp(self.tail, .5)

    @center.setter
    def center(self, val):
        print('RigBone.center is read-only!')

    @property
    def center_local(self) -> Vector:
        return self.head_local.lerp(self.tail_local, .5)

    @center_local.setter
    def center_local(self, val):
        print('RigBone.center_local is read-only!')

    @property
    def center_pose(self) -> Vector:
        return self.head_pose.lerp(self.tail_pose, .5)

    @center_pose.setter
    def center_pose(self, val):
        print('RigBone.center_pose is read-only!')

    @property
    def inherit_rotation(self):
        return self._armature_data.bones[self.bone.name].use_inherit_rotation

    @inherit_rotation.setter
    def inherit_rotation(self, value):
        self._armature_data.bones[self.bone.name].use_inherit_rotation = value

    @property
    def inherit_scale(self):
        return self._armature_data.bones[self.bone.name].inherit_scale

    @inherit_scale.setter
    def inherit_scale(self, value):
        self._armature_data.bones[self.bone.name].inherit_scale = value

    @property
    def connected(self):
        return self._armature_data.bones[self.bone.name].use_connect

    @connected.setter
    def connected(self, value):
        self._armature_data.bones[self.bone.name].use_connect = value

    @property
    def deform(self):
        return self._armature_data.bones[self.bone.name].use_deform

    @deform.setter
    def deform(self, value):
        self._armature_data.bones[self.bone.name].use_deform = value

    @property
    def use_local_location(self):
        return self._armature_data.bones[self.bone.name].use_local_location

    @use_local_location.setter
    def use_local_location(self, value):
        self._armature_data.bones[self.bone.name].use_local_location = value

    @property
    def use_relative_parent(self):
        return self._armature_data.bones[self.bone.name].use_relative_parent

    @use_relative_parent.setter
    def use_relative_parent(self, value):
        self._armature_data.bones[self.bone.name].use_relative_parent = value

    @property
    def use_scale_easing(self):
        return self._armature_data.bones[self.bone.name].use_scale_easing

    @use_scale_easing.setter
    def use_scale_easing(self, value):
        self._armature_data.bones[self.bone.name].use_scale_easing = value

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

    def visualize(self):
        for b in self.bones.values():
            st = b.world_space
            b.world_space = True
            # draw_line(b.head_pose, b.tail_pose, (.4, .88, .88))
            b.world_space = st

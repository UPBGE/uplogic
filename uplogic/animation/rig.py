from bge.types import BL_ArmatureChannel, BL_ArmatureObject
from bge.logic import ROT_MODE_QUAT, ROT_MODE_XYZ
from uplogic.utils.objects import GameObject
from mathutils import Vector, Quaternion, Matrix, Euler


class RigBone():

    def __init__(self, bone: BL_ArmatureChannel, armature: BL_ArmatureObject) -> None:
        self.bone = bone
        self.armature = armature
        self.bone.rotation_mode = ROT_MODE_XYZ

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
        self.bone.rotation_mode = ROT_MODE_XYZ
        self.bone.rotation_euler = Vector(val.to_euler())
        self.armature.blenderObject.update_tag()


class Rig(GameObject):

    def __init__(
        self,
        armature
    ) -> None:
        self.game_object: BL_ArmatureObject = armature
        self.bones: dict[str, RigBone] = {}
        for bone in self.game_object.channels:
            self.bones[bone.name] = RigBone(bone, armature)

    def set_bone_pos(self, bone: str, pos: Vector):
        self.bones[bone].worldPosition = pos

    def set_bone_rot(self, bone: str, rot: Quaternion):
        bone = self.game_object.channels[bone]
        bone.rotation_quaternion = bone.pose_matrix.inverted() @ Quaternion(rot)

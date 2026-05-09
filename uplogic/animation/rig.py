from bge.types import BL_ArmatureChannel, BL_ArmatureObject
from bge.logic import ROT_MODE_XYZ
from bpy.types import Bone
from uplogic import console
from uplogic.utils.objects import GameObject
from mathutils import Vector, Quaternion, Matrix, Euler
from uplogic.utils.visualize import draw_line


class RigBone():
    '''Convenience wrapper around a single ``BL_ArmatureChannel`` that exposes
    position, orientation, and Blender pose/rest-bone data through a unified
    property interface.

    :param bone: The BGE armature channel for this bone.
    :param armature: The ``BL_ArmatureObject`` that owns the bone.
    '''

    def __init__(self, bone: BL_ArmatureChannel, armature: BL_ArmatureObject) -> None:
        self.world_space = True
        self.bone = bone
        self.armature = armature
        self._armature_data = self.armature.blenderObject.data
        self._pose = self.armature.blenderObject.pose

    @property
    def attr_transform(self):
        '''World transform of the owning armature when :attr:`world_space` is
        ``True``, or an identity matrix otherwise (read-only).
        '''
        return self.armature.worldTransform if self.world_space else Matrix()

    @property
    def armature(self):
        '''The ``BL_ArmatureObject`` that owns this bone. Setting this also
        updates the internal Blender data and pose references.
        '''
        return self._armature

    @armature.setter
    def armature(self, val):
        self._armature_data = val.blenderObject.data
        self._armature = val

    @property
    def name(self):
        '''Name of this bone as reported by the BGE channel. Setting renames
        the underlying Blender bone.
        '''
        return self.bone.name

    @name.setter
    def name(self, val):
        self._armature_data.blenderObject.bones[self.bone.name].name = val

    @property
    def constraints(self):
        '''Constraint collection for this bone's pose bone (read-only).'''
        return self._pose.bones[self.bone.name].constraints

    @property
    def location(self):
        '''Pose-space location offset of this bone. Setting writes directly to
        the Blender pose bone.
        '''
        return self._pose.bones[self.bone.name].location

    @location.setter
    def location(self, val):
        self._pose.bones[self.bone.name].location = val

    @property
    def pose_rotation_euler(self):
        '''Euler rotation of this bone in pose space, always read in ``XYZ``
        order regardless of the bone's current rotation mode. Setting restores
        the original mode after writing.

        :returns: :class:`mathutils.Euler` in ``XYZ`` order.
        '''
        bone = self._pose.bones[self.bone.name]
        _mode = bone.rotation_mode
        # bone.rotation_mode = ROT_MODE_XYZ
        bone.rotation_mode = 'XYZ'
        res = bone.rotation_euler
        bone.rotation_mode = _mode
        return res

    @pose_rotation_euler.setter
    def pose_rotation_euler(self, euler: Euler):
        bone = self._pose.bones[self.bone.name]
        _mode = bone.rotation_mode
        # bone.rotation_mode = ROT_MODE_XYZ
        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = Euler(euler)
        self.armature.blenderObject.update_tag()
        bone.rotation_mode = _mode

    @property
    def head(self) -> Vector:
        '''Rest-pose head position in world space (or armature space when
        :attr:`world_space` is ``False``).
        '''
        return self.attr_transform @ self._armature_data.bones[self.bone.name].head

    @head.setter
    def head(self, value):
        self._armature_data.bones[self.bone.name].head = self.attr_transform.inverted() @ value

    @property
    def head_local(self) -> Vector:
        '''Rest-pose head position in the bone's local coordinate system.'''
        return self._armature_data.bones[self.bone.name].head_local

    @head_local.setter
    def head_local(self, value):
        self._armature_data.bones[self.bone.name].head_local = value

    @property
    def head_pose(self) -> Vector:
        '''Posed head position in world space (or armature space when
        :attr:`world_space` is ``False``).
        '''
        return self.attr_transform @ self._pose.bones[self.bone.name].head

    @head_pose.setter
    def head_pose(self, val):
        self._pose.bones[self.bone.name].head = self.attr_transform.inverted() @ val

    @property
    def tail(self) -> Vector:
        '''Rest-pose tail position in world space (or armature space when
        :attr:`world_space` is ``False``).
        '''
        return self.attr_transform @ self._armature_data.bones[self.bone.name].tail

    @tail.setter
    def tail(self, value):
        self._armature_data.bones[self.bone.name].tail = value

    @property
    def tail_local(self) -> Vector:
        '''Rest-pose tail position in the bone's local coordinate system.'''
        return self._armature_data.bones[self.bone.name].tail_local

    @tail_local.setter
    def tail_local(self, value):
        self._armature_data.bones[self.bone.name].tail_local = value

    @property
    def tail_pose(self) -> Vector:
        '''Posed tail position in world space (or armature space when
        :attr:`world_space` is ``False``).
        '''
        return self.attr_transform @ self._pose.bones[self.bone.name].tail

    @tail_pose.setter
    def tail_pose(self, val):
        self._pose.bones[self.bone.name].tail = val

    @property
    def center(self) -> Vector:
        '''Midpoint between :attr:`head` and :attr:`tail` in world (or armature)
        space (read-only).
        '''
        return self.head.lerp(self.tail, .5)

    @center.setter
    def center(self, val):
        console.debug('RigBone.center is read-only!')

    @property
    def center_local(self) -> Vector:
        '''Midpoint between :attr:`head_local` and :attr:`tail_local` in local
        bone space (read-only).
        '''
        return self.head_local.lerp(self.tail_local, .5)

    @center_local.setter
    def center_local(self, val):
        console.debug('RigBone.center_local is read-only!')

    @property
    def center_pose(self) -> Vector:
        '''Midpoint between :attr:`head_pose` and :attr:`tail_pose` in world
        (or armature) space (read-only).
        '''
        return self.head_pose.lerp(self.tail_pose, .5)

    @center_pose.setter
    def center_pose(self, val):
        console.debug('RigBone.center_pose is read-only!')

    @property
    def inherit_rotation(self):
        '''Whether this bone inherits rotation from its parent (``use_inherit_rotation``).'''
        return self._armature_data.bones[self.bone.name].use_inherit_rotation

    @inherit_rotation.setter
    def inherit_rotation(self, value):
        self._armature_data.bones[self.bone.name].use_inherit_rotation = value

    @property
    def inherit_scale(self):
        '''Scale inheritance mode from the parent bone (``inherit_scale``).'''
        return self._armature_data.bones[self.bone.name].inherit_scale

    @inherit_scale.setter
    def inherit_scale(self, value):
        self._armature_data.bones[self.bone.name].inherit_scale = value

    @property
    def connected(self):
        '''Whether this bone is connected to its parent (``use_connect``).'''
        return self._armature_data.bones[self.bone.name].use_connect

    @connected.setter
    def connected(self, value):
        self._armature_data.bones[self.bone.name].use_connect = value

    @property
    def deform(self):
        '''Whether this bone contributes to mesh deformation (``use_deform``).'''
        return self._armature_data.bones[self.bone.name].use_deform

    @deform.setter
    def deform(self, value):
        self._armature_data.bones[self.bone.name].use_deform = value

    @property
    def use_local_location(self):
        '''Whether the bone's location is in local rather than parent space.'''
        return self._armature_data.bones[self.bone.name].use_local_location

    @use_local_location.setter
    def use_local_location(self, value):
        self._armature_data.bones[self.bone.name].use_local_location = value

    @property
    def use_relative_parent(self):
        '''Whether the bone uses relative parent transformation.'''
        return self._armature_data.bones[self.bone.name].use_relative_parent

    @use_relative_parent.setter
    def use_relative_parent(self, value):
        self._armature_data.bones[self.bone.name].use_relative_parent = value

    @property
    def use_scale_easing(self):
        '''Whether scale easing is enabled for this bone.'''
        return self._armature_data.bones[self.bone.name].use_scale_easing

    @use_scale_easing.setter
    def use_scale_easing(self, value):
        self._armature_data.bones[self.bone.name].use_scale_easing = value

    @property
    def pose_matrix_cleaned(self):
        '''Pose matrix with the bone's own location and rotation offset removed,
        leaving only the contribution of parent transforms (read-only).
        '''
        offset_m4 = (Matrix.Translation(self.bone.location) @ Quaternion(self.bone.rotation_quaternion).to_matrix().to_4x4())
        return self.bone.pose_matrix @ offset_m4.inverted()

    @property
    def localPosition(self):
        '''Position of the bone in its parent's local space. Setting converts
        the supplied world-space value back through the armature and pose
        transforms and triggers a Blender data update.
        '''
        return self.bone.location @ self.bone.channel_matrix.inverted()

    @localPosition.setter
    def localPosition(self, val):
        self.bone.location = self.pose_matrix_cleaned.inverted() @ self.armature.worldTransform.inverted() @ (Vector(val) + self.armature.worldPosition)
        self.armature.blenderObject.update_tag()

    @property
    def worldPosition(self):
        '''World-space position of the bone's posed head. Equivalent to
        :attr:`head_pose` with :attr:`world_space` enabled.
        '''
        # w = self.world_space
        # self.world_space = True
        # res = self.head_pose
        # self.world_space = w
        return self.head_pose

    @worldPosition.setter
    def worldPosition(self, val):
        self.head_pose = val

    @property
    def worldOrientation(self):
        '''World-space orientation of the bone as an ``XYZ`` Euler, read from
        the BGE channel. The rotation mode is temporarily switched to
        ``ROT_MODE_XYZ`` and restored afterwards.

        :returns: :class:`mathutils.Euler` in ``XYZ`` order.
        '''
        _mode = self.bone.rotation_mode
        self.bone.rotation_mode = ROT_MODE_XYZ
        res = self.bone.rotation_euler
        self.bone.rotation_mode = _mode
        return res

    @worldOrientation.setter
    def worldOrientation(self, val: Matrix):
        _mode = self.bone.rotation_mode
        self.bone.rotation_mode = ROT_MODE_XYZ
        self.bone.rotation_euler = Vector(val.to_euler())
        self.armature.blenderObject.update_tag()
        self.bone.rotation_mode = _mode


class RigBones(dict):
    '''Typed ``dict`` mapping bone names to :class:`RigBone` instances.

    Inherits the full ``dict`` interface; no additional behaviour is added.
    '''
    pass


class Rig(GameObject):
    '''High-level wrapper around a ``BL_ArmatureObject`` that builds a
    :class:`RigBones` dictionary of :class:`RigBone` instances on construction
    and exposes helpers for driving bone positions and orientations at runtime.

    :param armature: The ``BL_ArmatureObject`` to wrap.
    '''

    def __init__(
        self,
        armature
    ) -> None:
        self.game_object: BL_ArmatureObject = armature
        self.bones: RigBones[str, RigBone] = RigBones()
        for bone in self.game_object.channels:
            self.bones[bone.name] = RigBone(bone, armature)

    def set_bone_pos(self, bone: str, pos: Vector):
        '''Set the world-space position of a bone by name.

        :param bone: Name of the bone to move.
        :param pos: Target world-space position.
        '''
        self.bones[bone].worldPosition = pos

    def set_bone_rot(self, bone: str, rot: Quaternion):
        '''Set the rotation of a bone by name, converting the supplied
        quaternion into the bone's local pose space.

        :param bone: Name of the bone to rotate.
        :param rot: Target rotation as a :class:`mathutils.Quaternion`.
        '''
        bone = self.game_object.channels[bone]
        bone.rotation_quaternion = bone.pose_matrix.inverted() @ Quaternion(rot)

    def visualize(self):
        '''Draw a debug line from the posed head to the posed tail of every
        bone in the rig using :func:`~uplogic.utils.visualize.draw_line`.
        '''
        for b in self.bones.values():
            st = b.world_space
            b.world_space = True
            draw_line(b.head_pose, b.tail_pose, (.4, .88, .88))
            b.world_space = st

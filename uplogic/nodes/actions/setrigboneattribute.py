from uplogic.nodes import ULActionNode
from uplogic.animation.rig import Rig, RigBone
from bge.logic import ROT_MODE_QUAT


class SetRigBoneAttributeNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.armature = None
        self.bone = None
        self.value = None
        self.attribute = 'inherit_rotation'
        self.scale_mode = 'FULL'
        self._rig: Rig = None
        self._done = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        armature = self.get_input(self.armature)
        if self._rig is None or self._rig.game_object is not armature:
            self._rig = Rig(armature)

        bone: RigBone = self._rig.bones[self.get_input(self.bone)]

        value = self.get_input(self.value)
        print(self.attribute, value, bone.name)
        setattr(bone, self.attribute, value if value is not None else self.scale_mode)
        for bone in self._rig.bones.values():
            print(bone.name, bone.inherit_rotation)
        # self._rig.blenderObject.update_tag()
        self._done = True

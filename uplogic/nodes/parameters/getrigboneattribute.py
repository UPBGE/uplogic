from uplogic.nodes import ULParameterNode
from uplogic.animation.rig import Rig, RigBone


class GetRigBoneAttributeNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.armature = None
        self.bone = None
        self.world_space = False
        self.VALUE = self.add_output(self.get_val)
        self.attribute = 'inherit_rotation'
        self._rig: Rig = None

    def get_val(self):
        armature = self.get_input(self.armature)
        if self._rig is None or self._rig.game_object is not armature:
            self._rig = Rig(armature)

        bone: RigBone = self._rig.bones[self.get_input(self.bone)]
        self._rig.visualize()
        bone.world_space = self.world_space
        return getattr(bone, self.attribute)

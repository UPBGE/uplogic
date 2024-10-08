from mathutils import Euler
from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.utils import debug


class ULSetBonePosition(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.armature = None
        self.bone_name = None
        self.set_translation = None
        self._eulers = Euler((0, 0, 0), "XYZ")
        self._vector = Vector((0, 0, 0))
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        armature = self.get_input(self.armature)
        bone_name = self.get_input(self.bone_name)
        set_translation = self.get_input(self.set_translation)
        # TODO cache the bone index
        bone_channel = armature.channels[bone_name]
        if set_translation is not None:
            bone_channel.location = set_translation
        else:
            debug('Set Bone Node: Position is None!')
        armature.update()
        self._done = True

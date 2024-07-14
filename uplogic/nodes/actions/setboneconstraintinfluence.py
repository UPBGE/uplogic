from uplogic.nodes import ULActionNode


class ULSetBoneConstraintInfluence(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.armature = None
        self.bone = None
        self.constraint = None
        self.influence = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        armature = self.get_input(self.armature)
        bone = self.get_input(self.bone)
        constraint = self.get_input(self.constraint)
        influence = self.get_input(self.influence)
        (
            armature
            .blenderObject
            .pose
            .bones[bone]
            .constraints[constraint]
            .influence
        ) = influence
        self._done = True

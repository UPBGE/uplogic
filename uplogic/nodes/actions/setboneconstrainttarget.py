from uplogic.nodes import ULActionNode


class ULSetBoneConstraintTarget(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.armature = None
        self.bone = None
        self.constraint = None
        self.target = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        armature = self.get_input(self.armature)
        bone = self.get_input(self.bone)
        constraint = self.get_input(self.constraint)
        target = self.get_input(self.target)
        (
            armature
            .blenderObject
            .pose
            .bones[bone]
            .constraints[constraint]
            .target
        ) = target.blenderObject
        self._done = True

from uplogic.nodes import ULActionNode


class ULSetBoneConstraintAttribute(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.armature = None
        self.bone = None
        self.constraint = None
        self.attribute = None
        self.value = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        armature = self.get_input(self.armature)
        bone = self.get_input(self.bone)
        constraint = self.get_input(self.constraint)
        attribute = self.get_input(self.attribute)
        value = self.get_input(self.value)
        setattr(
            (
                armature
                .blenderObject
                .pose
                .bones[bone]
                .constraints[constraint]
            ),
            attribute, value
        )
        self._done = True

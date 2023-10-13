from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetBoneConstraintAttribute(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.armature = None
        self.bone = None
        self.constraint = None
        self.attribute = None
        self.value = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
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
        self.done = True

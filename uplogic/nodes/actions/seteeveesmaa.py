from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
import bpy


class ULSetEeveeSMAA(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.value = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if self.get_input(self.condition):
            print("SMAA has been removed from UPBGE. Delete 'Set SMAA' node to avoid issues.")
            self.done = True

from bge import logic
from uplogic.nodes import ULActionNode
import bpy


class ULSetEeveeSMAAQuality(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.value = None
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        print("SMAA has been removed from UPBGE. Delete 'Set SMAA Quality' node to avoid issues.")
        self.done = True
        

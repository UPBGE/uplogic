from uplogic.data import GlobalDB
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetGlobalValue(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.data_id = None
        self.key = None
        self.value = None
        self.persistent = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        data_id = self.get_input(self.data_id)
        persistent = self.get_input(self.persistent)
        key = self.get_input(self.key)
        value = self.get_input(self.value)
        db = GlobalDB.retrieve(data_id)
        db.put(key, value, persistent)
        self.done = True

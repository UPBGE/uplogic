from uplogic.data import GlobalDB
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULGetGlobalValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.data_id = None
        self.key = None
        self.default = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        data_id = self.get_input(self.data_id)
        key = self.get_input(self.key)
        default = self.get_input(self.default)
        db = GlobalDB.retrieve(data_id)
        return db.get(key, default)

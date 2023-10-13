from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetDictKey(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.dict = None
        self.key = None
        self.val = None
        self.new_dict = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.DICT = ULOutSocket(self, self.get_dict)

    def get_done(self):
        return self.done

    def get_dict(self):
        return self.new_dict

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        dictionary = self.get_input(self.dict)
        key = self.get_input(self.key)
        val = self.get_input(self.val)
        dictionary[key] = val
        self.new_dict = dictionary
        self.done = True

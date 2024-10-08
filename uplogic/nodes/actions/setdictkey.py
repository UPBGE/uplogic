from uplogic.nodes import ULActionNode


class ULSetDictKey(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.dict = None
        self.key = None
        self.val = None
        self.new_dict = None
        self.OUT = self.add_output(self.get_done)
        self.DICT = self.add_output(self.get_dict)

    def get_done(self):
        return self._done

    def get_dict(self):
        return self.new_dict

    def evaluate(self):
        if not self.get_condition():
            return
        dictionary = self.get_input(self.dict)
        key = self.get_input(self.key)
        val = self.get_input(self.val)
        dictionary[key] = val
        self.new_dict = dictionary
        self._done = True

from uplogic.data import GlobalDB
from uplogic.nodes import ULActionNode
from uplogic import console


class ULListGlobalValues(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.data_id = None
        self.print_d = None
        self.gv_dict = None
        self.OUT = self.add_output(self.get_done)
        self.VALUE = self.add_output(self.get_dict)

    def get_done(self):
        return self._done

    def get_dict(self):
        return self.gv_dict

    def evaluate(self):
        if not self.get_condition():
            return
        data_id = self.get_input(self.data_id)
        print_d = self.get_input(self.print_d)
        db = GlobalDB.retrieve(data_id)
        if print_d:
            console.log(f'[Logic Nodes] Global category "{data_id}":')
            for e in db.data:
                console.log('{}\t->\t{}'.format(e, db.data[e]))
            console.log('END ------------------------------------')
        self._done = True
        self.gv_dict = db.data

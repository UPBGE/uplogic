from uplogic.nodes import ULActionNode
from bge.logic import getRealTime


class ULGetPerformanceProfile(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.network = None
        self.print_profile = False
        self.check_evaluated_cells = False
        self.check_average_cells_per_sec = False
        self.check_cells_per_tick = False
        self.data = ''
        self.OUT = self.add_output(self.get_done)
        self.DATA = self.add_output(self.get_data)

    def get_done(self):
        return self._done

    def get_data(self):
        return self.data

    def setup(self, network):
        self.network = network

    def evaluate(self):
        self.data = '----------------------------------Start Profile\n'
        if not self.get_condition():
            return
        print_profile = self.get_input(
            self.print_profile
        )
        check_evaluated_cells = self.get_input(
            self.check_evaluated_cells
        )
        check_average_cells_per_sec = self.get_input(
            self.check_average_cells_per_sec
        )
        check_cells_per_tick = self.get_input(
            self.check_cells_per_tick
        )
        if check_evaluated_cells:
            self.data += 'Evaluated Nodes:\t{}\n'.format(
                self.network.evaluated_cells
            )
        if check_average_cells_per_sec:
            self.data += 'Nodes per Sec (avg):\t{}\n'.format(
                self.network.evaluated_cells / getRealTime()
            )
        if check_cells_per_tick:
            self.data += 'Nodes per Tick:\t{}\n'.format(
                len(self.network._cells)
            )
        self.data += '----------------------------------End Profile'
        if print_profile:
            print(self.data)
        self._done = True

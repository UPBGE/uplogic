from bge import events
from bge import logic
from bge.types import KX_GameObject as GameObject
from uplogic.audio import AudioSystem
from uplogic.data import GlobalDB
from uplogic.nodes import ULLogicContainer
from uplogic.utils import load_user_module
from uplogic.utils import make_valid_name
from uplogic.data import init_glob_cats
import bpy
# from uplogic import get_mainloop
from bge.types import SCA_PythonKeyboard as Keyboard
import collections
from bge.logic import getRealTime
from uplogic import console


class ULLogicTree(ULLogicContainer):

    def __init__(self):
        from ..input import Mouse
        ULLogicContainer.__init__(self)
        self._cells: list = []
        self._iter = collections.deque()
        self._lastuid: int = 0
        self.component = {}
        self._owner: GameObject = None
        self._initialized = False
        self._max_blocking_loop_count: int = 0
        self.keyboard: Keyboard = None
        self.mouse: Mouse = Mouse()
        self.mouse_events = None
        self.stopped = False
        self._time_then = getRealTime()
        self.time_per_frame = 0.0
        self._do_remove = False
        self.aud_system_owner = False
        init_glob_cats()
        self.audio_system = self.get_aud_system()
        self.sub_networks = []  # a list of networks updated by this network
        self.capslock_pressed = False
        self.evaluated_cells = 0
        # scene = self.scene = logic.getCurrentScene()
        mainloop = logic.globalDict.get('loop')
        if mainloop:
            mainloop.logic_tree = self

    @property
    def owner(self):
        return self._owner

    def get_aud_system(self):
        aud_sys = GlobalDB.retrieve('uplogic.audio').get('default')
        if not aud_sys:
            self.aud_system_owner = True
            return AudioSystem('default')
        return aud_sys

    def set_mouse_position(self, screen_x, screen_y):
        self.mouse.position = (screen_x, screen_y)

    def get_owner(self):
        return self._owner

    def setup(self):
        self.time_per_frame = 0.0
        for cell in self._cells:
            cell.network = self
            cell.setup(self)

    def is_running(self):
        return not self.stopped

    def is_stopped(self):
        return self.stopped

    def stop(self, network=None):
        if self.stopped:
            return
        # self._time_then = None  # XXX: Was this important? Causes issues when stopping and restarting
        self.stopped = True
        for cell in self._cells:
            cell.stop(self)

    def _generate_cell_uid(self):
        self._lastuid += 1
        return self._lastuid

    def add_cell(self, cell):
        self._cells.append(cell)
        self._iter.append(cell)
        self._max_blocking_loop_count = len(self._cells) * len(self._cells)
        cell._uid = self._generate_cell_uid()
        return cell

    def evaluate(self):
        now = getRealTime()
        dtime = now - self._time_then
        self._time_then = now
        self.time_per_frame = dtime
        if self._owner.invalid:
            console.debug("Network Owner removed from game. Shutting down the network")
            return True
        self.keyboard = logic.keyboard
        self.keyboard_events = self.keyboard.inputs.copy()
        caps_lock_event = self.keyboard_events[events.CAPSLOCKKEY]
        if(caps_lock_event.released):
            self.capslock_pressed = not self.capslock_pressed
        # update the cells
        cells = self._iter.copy()
        while cells:
            cell = cells.popleft()
            cell.evaluate()
        for cell in self._cells:
            cell.reset()
        self._initialized = True
        for network in self.sub_networks:
            if network._owner.invalid:
                self.sub_networks.remove(network)
            elif not network.stopped:
                network.evaluate()

    def install_subnetwork(self, owner_object, node_tree_name, initial_status):
        # transform the tree name into a NL module name
        tree_name = make_valid_name(node_tree_name)
        mname = f'nl_{tree_name.lower()}'
        module = load_user_module(mname)
        owner_object[f'NL__{tree_name}'] = initial_status
        tree = module.get_tree(owner_object).network
        owner_object[f'IGNLTree_{tree_name}'] = tree
        self.sub_networks.append(tree)
        tree.stopped = not initial_status
        return tree

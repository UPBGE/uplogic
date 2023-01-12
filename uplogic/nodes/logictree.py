from bge import events
from bge import logic as bgelogic
from bge.types import KX_GameObject as GameObject
from uplogic.audio import ULAudioSystem
from uplogic.data import GlobalDB
from uplogic.nodes import STATUS_READY
from uplogic.nodes import STATUS_WAITING
from uplogic.nodes import ULLogicContainer
from uplogic.utils import debug
from uplogic.utils import load_user_module
from uplogic.utils import make_valid_name
import bpy
# from uplogic import get_mainloop
from uplogic.utils.nodes import evaluate_cells
from bge.types import SCA_PythonKeyboard as Keyboard
from bge.types import SCA_PythonMouse as Mouse
import collections
import time



class ULLogicTree(ULLogicContainer):

    def __init__(self):
        from ..input import ULMouse
        ULLogicContainer.__init__(self)
        self._cells: list = []
        self._iter: collections.deque = collections.deque()
        self._lastuid: int = 0
        self._owner: GameObject = None
        self._max_blocking_loop_count: int = 0
        self.keyboard: Keyboard = None
        # self.mouse: Mouse = None
        self.mouse: ULMouse = ULMouse()
        self.keyboard_events = None
        self.active_keyboard_events = None
        self.mouse_events = None
        self.stopped = False
        self.timeline = 0.0
        self._time_then = None
        self.time_per_frame = 0.0
        self._do_remove = False
        self.aud_system_owner = False
        self.init_glob_cats()
        self.audio_system = self.get_aud_system()
        self.sub_networks = []  # a list of networks updated by this network
        self.capslock_pressed = False
        self.evaluated_cells = 0
        scene = bgelogic.getCurrentScene()
        mainloop = scene.get('uplogic.mainloop')
        if mainloop:
            mainloop.logic_tree = self

    def get_aud_system(self):
        aud_sys = GlobalDB.retrieve('uplogic.audio').get('default')
        if not aud_sys:
            self.aud_system_owner = True
            return ULAudioSystem('default')
        return aud_sys

    def init_glob_cats(self):
        if not hasattr(bpy.types.Scene, 'nl_globals_initialized'):
            scene = bgelogic.getCurrentScene()
            cats = getattr(
                bpy.data.scenes[scene.name],
                'nl_global_categories',
                None
            )
            if not cats:
                return

            msg = ''

            dat = {
                'STRING': 'string_val',
                'FLOAT': 'float_val',
                'INTEGER': 'int_val',
                'BOOLEAN': 'bool_val',
                'FILE_PATH': 'filepath_val'
            }

            for c in cats:
                db = GlobalDB.retrieve(c.name)
                msg += f' {c.name},'
                for v in c.content:
                    val = getattr(v, dat.get(v.value_type, 'FLOAT'), 0)
                    db.put(v.name, val, v.persistent)

            if msg:
                debug(f'Globals Initialized:{msg[:-1]}')
            bpy.types.Scene.nl_globals_initialized = True

    def ray_cast(
        self,
        caster_object,
        ray_origin,
        ray_destination,
        property,
        xray,
        distance
    ):
        now = time.time()
        cached_data = caster_object.get("_NL_ray_cast_data")
        if cached_data is not None:
            data_time = cached_data[0]
            data_origin = cached_data[1]
            data_destination = cached_data[2]
            data_property = cached_data[3]
            data_distance = cached_data[4]
            d_time = now - data_time
            # only if we are in the same frame,
            # otherwise scenegraph might have changed
            if d_time < 0.01:
                if (
                    (data_origin == ray_origin) and
                    (data_destination == ray_destination) and
                    (data_property == property) and
                    (data_distance == distance)
                ):
                    return cached_data[5]
            pass
        obj, point, normal = None, None, None
        if property is not None:
            obj, point, normal = caster_object.rayCast(
                ray_destination,
                ray_origin,
                distance,
                property,
                xray=xray
            )
        else:
            obj, point, normal = caster_object.rayCast(
                ray_destination,
                ray_origin,
                distance,
                xray=xray
            )
        cached_data = (
            now,
            ray_origin,
            ray_destination,
            property,
            distance,
            (obj, point, normal)
        )
        caster_object["_NL_ray_cast_data"] = cached_data
        return obj, point, normal

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
        self._time_then = None
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
        now = time.time()
        if self._time_then is None:
            self._time_then = now
        dtime = now - self._time_then
        self._time_then = now
        self.timeline += dtime
        self.time_per_frame = dtime
        if self._owner.invalid:
            print("Network Owner removed from game. Shutting down the network")
            return True
        self.keyboard = bgelogic.keyboard
        self.keyboard_events = self.keyboard.inputs.copy()
        self.active_keyboard_events = self.keyboard.activeInputs.copy()
        caps_lock_event = self.keyboard_events[events.CAPSLOCKKEY]
        if(caps_lock_event.released):
            self.capslock_pressed = not self.capslock_pressed

        # update the cells
        cells = self._iter
        max_loop_count = len(cells)
        loop_index = 0
        done_cells = []
        max_blocking_loop_count = self._max_blocking_loop_count
        # now = time.time()
        # print('Heööp')
        # evaluate_cells(
        #     self, self._iter, self._max_blocking_loop_count
        # )

        while cells:
            if loop_index == max_blocking_loop_count:
                debug(
                    "Network found a blocking condition" +
                    " (due to unconnected or non responsive cell)"
                )
                debug("Stopping network...")
                self.stop()
                return
            cell = cells.popleft()
            if cell in done_cells:
                continue
            else:
                done_cells.append(cell)
            cell.evaluate()
            self.evaluated_cells += 1
            if not cell.has_status(STATUS_READY):
                cells.append(cell)
            loop_index += 1
        done_cells = []
        if(loop_index > max_loop_count):
            debug(
                "Wrong sorting alghorithm!",
                loop_index,
                max_loop_count
            )
        for cell in self._cells:
            cell.reset()
            if cell.has_status(STATUS_WAITING):
                cells.append(cell)
        # pulse subnetworks
        for network in self.sub_networks:
            if network._owner.invalid:
                self.sub_networks.remove(network)
            elif not network.stopped:
                network.evaluate()

        # newnow = time.time()
        # print('############################')
        # print(newnow - now)

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

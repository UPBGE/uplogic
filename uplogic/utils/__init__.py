'''TODO: Documentation
'''
from .lights import ULLight, Light  # noqa
from .lights import make_unique_light  # noqa
from .nodetrees import get_geom_socket  # noqa
from .nodetrees import get_group_socket  # noqa
from .nodetrees import get_material_socket  # noqa
from .nodetrees import get_world_socket  # noqa
from .nodetrees import modify_geom_socket  # noqa
from .nodetrees import modify_material_socket  # noqa
from .nodetrees import modify_world_socket  # noqa
from .nodetrees import set_geom_socket  # noqa
from .nodetrees import set_group_socket  # noqa
from .nodetrees import set_material_socket  # noqa
from .nodetrees import set_world_socket  # noqa
from .objects import get_curve_length
from .objects import ULCurve, Curve  # noqa
from .objects import controller_brick_status  # noqa
from .objects import controller_brick  # noqa
from .objects import create_curve  # noqa
from .objects import set_curve_points  # noqa
from .raycasting import raycast  # noqa
from .raycasting import raycast_camera  # noqa
from .raycasting import raycast_face  # noqa
from .raycasting import raycast_projectile  # noqa
from .raycasting import raycast_mouse  # noqa
from .scene import set_scene  # noqa
from .pooling import SpawnPool  # noqa
from .pooling import Spawn  # noqa
from .pooling import SimpleBullet  # noqa
from .pooling import PhysicsBullet  # noqa
from .visuals import draw_box  # noqa
from .visuals import draw_cube  # noqa
from .visuals import draw_line  # noqa
from .visuals import draw_points  # noqa
from .scene import FileLoader  # noqa
from .scene import SceneLoader  # noqa
from .math import clamp
from .math import cycle
from .math import vec_abs
from .math import vec_clamp
from .math import interpolate
from .math import lerp
from .math import get_angle
from .math import get_bitmask
from .math import get_collision_bitmask
from .math import get_direction
from .math import get_local
from .math import get_raw_angle
from .math import map_range
from .math import mouse_over
from .math import screen_to_world
from .math import world_to_screen
from .math import rotate2d
from .math import rotate3d
from .math import rotate_by_axis
from .objects import xrot_to
from .objects import yrot_to
from .objects import zrot_to
from .objects import rotate_to
from .constants import WATER
from .constants import OPERATORS
from .constants import LOGIC_OPERATORS
from .constants import RED
from .constants import GREEN
from .constants import BLUE
from .constants import YELLOW
from .constants import PURPLE
from .constants import TORQUISE
from .constants import WHITE
from .constants import BLACK
from .constants import GREY
from .constants import FPS_FACTOR
from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Matrix
from mathutils import Vector
import time as t

import bpy
import json
import math


###############################################################################
# LOGIC NODES
###############################################################################


def _name_query(named_items, query):
    assert len(query) > 0
    postfix = (query[0] == "*")
    prefix = (query[-1] == "*")
    infix = (prefix and postfix)
    if infix:
        token = query[1:-1]
        for item in named_items:
            if token in item.name:
                return item
    if prefix:
        token = query[:-1]
        for item in named_items:
            if item.name.startswith(token):
                return item
    if postfix:
        token = query[1:]
        for item in named_items:
            if item.name.endswith(token):
                return item
    for item in named_items:
        if item.name == query:
            return item
    return None


def check_game_object(query, scene=None):
    '''TODO: Documentation
    '''
    if not scene:
        scene = logic.getCurrentScene()
    else:
        scene = scene
    if (query is None) or (query == ""):
        return
    if not is_invalid(scene):
        # find from scene
        return _name_query(scene.objects, query)


def compute_distance(parama, paramb) -> float:
    '''TODO: Documentation
    '''
    if is_invalid(parama):
        return None
    if is_invalid(paramb):
        return None
    if hasattr(parama, "getDistanceTo"):
        return parama.getDistanceTo(paramb)
    if hasattr(paramb, "getDistanceTo"):
        return paramb.getDistanceTo(parama)
    va = Vector(parama)
    vb = Vector(paramb)
    return (va - vb).length


def debug(message: str):
    if not hasattr(bpy.types.Scene, 'logic_node_settings'):
        return
    if not bpy.context or not bpy.context.scene:
        return
    if not bpy.context.scene.logic_node_settings.use_node_debug:
        return
    else:
        print('[UPLOGIC] ' + message)


def is_invalid(*a) -> bool:
    for ref in a:
        if ref is None or ref == '':
            return True
        if not hasattr(ref, "invalid"):
            continue
        elif ref.invalid:
            return True
    return False


def make_valid_name(name):
    valid_characters = (
        "_abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    clsname = name.replace(' ', '_')
    stripped_name = "".join(
        [c for c in clsname if c in valid_characters]
    )
    return stripped_name


def not_met(*conditions) -> bool:
    for c in conditions:
        if (
            c is None or
            c is False
        ):
            return True
    return False


def load_user_module(module_name):
    import sys
    exec(f"import {module_name}")
    return sys.modules[module_name]


def unload_nodes(a, b):
    if not hasattr(bpy.types.Scene, 'nl_globals_initialized'):
        return
    delattr(bpy.types.Scene, 'nl_globals_initialized')


###############################################################################
# SCENE
###############################################################################


def get_closest_instance(game_obj: GameObject, name: str):
    '''TODO: Documentation
    '''
    objs = []
    distances = {}
    for obj in logic.getCurrentScene().objects:
        if obj.name == name:
            objs.append(obj)
    for obj in objs:
        distances[game_obj.getDistanceTo(obj)] = obj
    return distances[min(distances.keys())]


def is_water(game_object: GameObject):
    return WATER in game_object.getPropertyNames()


def get_child_by_name(obj, child, recursive=True, partial=False):
    children = obj.childrenRecursive if recursive else obj.children
    if partial:
        for c in children:
            if child in c.name:
                return c
    else:
        return children.get(child)


def check_vr_session_status() -> tuple[Vector, Matrix]:
    """Get the current position and orientation of connected VR headset.
    :returns: `tuple` of (`Vector`, `Matrix`)
    """
    session = bpy.context.window_manager.xr_session_state
    return session is not None

'''Top-level utility re-exports and scene helper functions for uplogic.

Provides game-object queries, math helpers, raycasting, scene management,
object pooling, visualisation primitives, and compile-time constants.
All public symbols from the sub-modules are re-exported here so that
``from uplogic.utils import <name>`` works without knowing the sub-module.
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
from .objects import Mesh  # noqa
from .objects import controller_brick_status  # noqa
from .objects import controller_brick  # noqa
from .objects import create_curve  # noqa
from .objects import set_curve_points  # noqa
from .raycasting import raycast  # noqa
from .raycasting import raycast_screen  # noqa
from .raycasting import raycast_camera  # noqa
from .raycasting import raycast_face  # noqa
from .raycasting import raycast_projectile  # noqa
from .raycasting import raycast_mouse  # noqa
from .scene import set_scene  # noqa
from .scene import get_custom_loop  # noqa
from .pooling import SpawnPool  # noqa
from .pooling import Spawn  # noqa
from .pooling import SimpleBullet  # noqa
from .pooling import PhysicsBullet  # noqa
from .visualize import draw_box  # noqa
from .visualize import draw_cube  # noqa
from .visualize import draw_line  # noqa
from .visualize import draw_path  # noqa
from .visualize import draw_mesh  # noqa
from .visualize import draw_arrow  # noqa
from .visualize import draw_arrow_path  # noqa
from .visualize import draw_axis  # noqa
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
from .scene import screen_to_world
from .scene import world_to_screen
from .math import rotate2d
from .math import rotate3d
from .math import rotate_by_axis
from .math import rotate_by_euler
from .objects import xrot_to
from .objects import yrot_to
from .objects import zrot_to
from .objects import rotate_to
from .constants import WATER
from .constants import OPERATORS
from .constants import MATH_OPERATORS
from .constants import LOGIC_OPERATORS
from .constants import RED
from .constants import GREEN
from .constants import BLUE
from .constants import YELLOW
from .constants import PURPLE
from .constants import TORQUISE
from .constants import WHITE
from .constants import BLACK
from .constants import ORANGE
from .constants import GREY
from .constants import FPS_FACTOR
from .constants import DELTA_TIME
from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Matrix
from mathutils import Vector
import time as t
from os import path, pardir

import bpy
import json
import math


# class classproperty(object):
#     def __init__(self, f):
#         self.f = f

#     def __get__(self, obj, owner):
        # return self.f(owner)


###############################################################################
# LOGIC NODES
###############################################################################


def _name_query(named_items, query):
    '''Search a list of named items using an exact or wildcard pattern.

    The *query* string controls matching behaviour:

    - Exact: ``"token"`` — matches items whose ``name`` equals *query* exactly.
    - Prefix (suffix wildcard): ``"token*"`` — matches items whose ``name``
      starts with ``"token"``.
    - Suffix (prefix wildcard): ``"*token"`` — matches items whose ``name``
      ends with ``"token"``.
    - Infix (both wildcards): ``"*token*"`` — matches items whose ``name``
      contains ``"token"``.

    :param named_items: Iterable of objects that each expose a ``.name``
        attribute (e.g. a BGE scene ``objects`` list).
    :param query: Non-empty search string, optionally surrounded by ``*``
        wildcards.
    :returns: The first matching item, or ``None`` if no match is found.
    :raises AssertionError: If *query* is an empty string.
    '''
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
    '''Look up a game object in the active scene by name query.

    Uses ``_name_query`` internally, so *query* may include ``*`` wildcards
    for prefix, suffix, or infix matching. When *scene* is omitted the
    current BGE scene is used.

    :param query: Name or wildcard pattern to search for. Passing ``None``
        or an empty string returns ``None`` immediately.
    :param scene: Optional BGE scene to search. Defaults to
        ``logic.getCurrentScene()``.
    :returns: The first matching ``KX_GameObject``, or ``None`` if not found
        or if *scene* is invalid.
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
    '''Return the distance between two objects or vectors.

    Tries ``getDistanceTo`` on *parama* first, then on *paramb*, and falls
    back to constructing ``Vector`` instances and computing the length of
    their difference. Returns ``None`` when either argument is invalid
    (as determined by ``is_invalid``).

    :param parama: A BGE game object supporting ``getDistanceTo``, or any
        sequence that can be passed to ``Vector()``.
    :param paramb: A BGE game object supporting ``getDistanceTo``, or any
        sequence that can be passed to ``Vector()``.
    :returns: The scalar distance as a ``float``, or ``None`` if either
        argument is invalid.
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


# def debug(message: str):
#     if not hasattr(bpy.types.Scene, 'logic_node_settings'):
#         return
#     if not bpy.context or not bpy.context.scene:
#         return
#     if not bpy.context.scene.logic_node_settings.use_node_debug:
#         return
#     else:
#         print('[UPLOGIC] ' + message)


def is_invalid(*a) -> bool:
    '''Return ``True`` if any argument is considered invalid.

    An argument is invalid when it is ``None``, an empty string ``""``, or a
    BGE object whose ``.invalid`` attribute is ``True``. Objects that do not
    have an ``.invalid`` attribute are considered valid.

    :param a: One or more values to test.
    :returns: ``True`` if at least one argument is invalid, ``False``
        otherwise.
    '''
    for ref in a:
        if ref is None or ref == '':
            return True
        if not hasattr(ref, "invalid"):
            continue
        elif ref.invalid:
            return True
    return False


def make_valid_name(name):
    '''Strip non-identifier characters from a string and return a valid name.

    Spaces in *name* are replaced with underscores first; all remaining
    characters that are not ASCII letters, digits, or underscores are
    removed. The result is safe to use as a Python identifier or attribute
    name.

    :param name: Arbitrary string to sanitise.
    :returns: A string containing only characters from
        ``[A-Za-z0-9_]``.
    '''
    valid_characters = (
        "_abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    clsname = name.replace(' ', '_')
    stripped_name = "".join(
        [c for c in clsname if c in valid_characters]
    )
    return stripped_name


def not_met(*conditions) -> bool:
    '''Return ``True`` if any condition is unmet.

    A condition is considered unmet when it is ``None`` or ``False``.
    Useful as a guard that short-circuits as soon as one prerequisite fails.

    :param conditions: One or more values to evaluate.
    :returns: ``True`` if at least one condition is ``None`` or ``False``,
        ``False`` if all conditions are truthy.
    '''
    for c in conditions:
        if (
            c is None or
            c is False
        ):
            return True
    return False


def load_user_module(module_name):
    '''Import a user module by name and return it.

    Executes ``import <module_name>`` in the current scope and retrieves the
    resulting module object from ``sys.modules``. The module must be
    importable from the current ``sys.path``.

    :param module_name: Fully-qualified module name string, e.g.
        ``"mypackage.mymodule"``.
    :returns: The imported module object.
    '''
    import sys
    exec(f"import {module_name}")
    return sys.modules[module_name]


def unload_nodes(a, b):
    '''Remove the ``nl_globals_initialized`` attribute from ``bpy.types.Scene``.

    Intended for use as a ``load_post`` handler so that node-logic global
    state is reset whenever a new blend file is loaded. Does nothing if the
    attribute is not present.

    :param a: First handler argument (blend file path string) — unused.
    :param b: Second handler argument (use-defaults flag) — unused.
    '''
    if not hasattr(bpy.types.Scene, 'nl_globals_initialized'):
        return
    delattr(bpy.types.Scene, 'nl_globals_initialized')


###############################################################################
# SCENE
###############################################################################


def get_closest_instance(game_obj: GameObject, name: str):
    '''Return the scene object with the given name that is nearest to *game_obj*.

    All objects in the current scene whose ``name`` matches *name* exactly
    are collected, and the one with the smallest ``getDistanceTo`` value
    relative to *game_obj* is returned.

    :param game_obj: The reference ``KX_GameObject`` from which distances are
        measured.
    :param name: Exact name of the target objects to search for.
    :returns: The ``KX_GameObject`` instance closest to *game_obj*.
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
    '''Return ``True`` if *game_object* is tagged as a water surface.

    Checks whether the internal ``WATER`` game-property key is present in
    the object's property list.

    :param game_object: The ``KX_GameObject`` to inspect.
    :returns: ``True`` if the ``WATER`` property exists on the object,
        ``False`` otherwise.
    '''
    return WATER in game_object.getPropertyNames()


def get_child_by_name(obj: GameObject, child: str, recursive: bool = True, partial: bool = False) -> GameObject:
    '''Find a child of *obj* by name.

    :param obj: The parent ``KX_GameObject`` whose children are searched.
    :param child: Name (or substring when *partial* is ``True``) to search for.
    :param recursive: When ``True``, the search descends into
        ``obj.childrenRecursive``; when ``False``, only direct
        ``obj.children`` are checked.
    :param partial: When ``True``, any child whose name *contains* the
        *child* string is accepted as a match. When ``False``, the name must
        match exactly.
    :returns: The first matching child ``KX_GameObject``, or ``None`` if no
        child matches.
    '''
    children = obj.childrenRecursive if recursive else obj.children
    if partial:
        for c in children:
            if child in c.name:
                return c
    else:
        return children.get(child)


def check_vr_session_status() -> bool:
    '''Return ``True`` if a VR/XR session is currently active.

    Reads ``bpy.context.window_manager.xr_session_state`` and treats a
    non-``None`` value as an active session.

    :returns: ``True`` when an XR session is running, ``False`` otherwise.
    '''
    session = bpy.context.window_manager.xr_session_state
    return session is not None


def get_project_path(folder_name, *structure):
    '''Walk up the directory tree to find a named folder and build a path inside it.

    Starting from the blend file's directory (``bpy.path.abspath('//')``),
    the function traverses parent directories until a directory named
    *folder_name* is found. The remaining *structure* components are then
    joined onto that directory with ``os.path.join``.

    :param folder_name: Name of the ancestor directory to locate.
    :param structure: Zero or more path components to join after *folder_name*
        (passed directly to ``os.path.join``).
    :returns: The resolved path string, or ``''`` if the filesystem root is
        reached before *folder_name* is found (an error is also logged).
    '''
    from uplogic.console import error
    directory = og_path = path.join(bpy.path.abspath('//'))[:-1]
    while not directory.endswith(folder_name):
        # print(folder_name)
        pdir = path.abspath(path.join(directory, pardir))
        if pdir == directory:
            error(f"Can't go beyond drive's root from {og_path}!")
            return ''
        directory = pdir
    return path.join(directory, *structure)

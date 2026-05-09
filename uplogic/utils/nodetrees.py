'''Node-tree socket accessor helpers for uplogic. Provides get/set/modify
functions for node group, material, world, and geometry node trees.
'''
from bge.types import KX_GameObject as GameObject
from bpy.types import Material
from bpy.types import Node
from bpy.types import NodeSocket
from bpy.types import NodeGroup
import bpy


def get_group_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket
):
    '''Return the ``default_value`` of an input socket in a node group.

    :param tree: name string or ``NodeGroup`` instance
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``

    :returns: current ``default_value`` of the socket
    '''
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    return (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    )


def set_group_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket,
    value
):
    '''Set the ``default_value`` of an input socket in a node group.

    :param tree: name string or ``NodeGroup`` instance
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: new value to assign
    '''
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) = value


def modify_group_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket,
    value
):
    '''Add *value* to the ``default_value`` of an input socket in a node group.

    :param tree: name string or ``NodeGroup`` instance
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: amount to add to the current socket value
    '''
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) += value


def get_geom_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket
):
    '''Return the ``default_value`` of an input socket in a geometry node group.

    :param tree: name string or ``NodeGroup`` instance
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``

    :returns: current ``default_value`` of the socket
    '''
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    return (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    )


def set_geom_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket,
    value
):
    '''Set the ``default_value`` of an input socket in a geometry node group.

    :param tree: name string or ``NodeGroup`` instance
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: new value to assign
    '''
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) = value


def modify_geom_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket,
    value
):
    '''Add *value* to the ``default_value`` of an input socket in a geometry
    node group.

    :param tree: name string or ``NodeGroup`` instance
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: amount to add to the current socket value
    '''
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) += value


def get_material_socket(
    material: str or Material,
    node: Node,
    socket: NodeSocket,
    game_object: GameObject = None
):
    '''Return the ``default_value`` of an input socket in a material node tree.

    *material* may be a name string, a ``Material`` data-block, or a slot
    index integer. When an integer is given, *game_object* is required to
    resolve the material from the object's material slots.

    :param material: name string, ``Material``, or slot index int
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param game_object: ``KX_GameObject`` used to resolve a slot-index material
                        (default ``None``)

    :returns: current ``default_value`` of the socket
    '''
    if isinstance(material, str):
        material = bpy.data.materials[material]
    if isinstance(material, int):
        material = game_object.blenderObject.material_slots[0].material
    return (
        material
        .node_tree
        .nodes[node]
        .inputs[socket]
        .default_value
    )


def set_material_socket(
    material: str or Material,
    node: Node,
    socket: NodeSocket,
    value,
    game_object: GameObject = None
):
    '''Set the ``default_value`` of an input socket in a material node tree.

    *material* may be a name string, a ``Material`` data-block, or a slot
    index integer. When an integer is given, *game_object* is required to
    resolve the material from the object's material slots.

    :param material: name string, ``Material``, or slot index int
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: new value to assign
    :param game_object: ``KX_GameObject`` used to resolve a slot-index material
                        (default ``None``)
    '''
    if isinstance(material, str):
        material = bpy.data.materials[material]
    if isinstance(material, int):
        material = game_object.blenderObject.material_slots[0].material
    (
        material
        .node_tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) = value


def modify_material_socket(
    material: str or Material,
    node: Node,
    socket: NodeSocket,
    value,
    game_object: GameObject = None
):
    '''Add *value* to the ``default_value`` of an input socket in a material
    node tree.

    *material* may be a name string, a ``Material`` data-block, or a slot
    index integer. When an integer is given, *game_object* is required to
    resolve the material from the object's material slots.

    :param material: name string, ``Material``, or slot index int
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: amount to add to the current socket value
    :param game_object: ``KX_GameObject`` used to resolve a slot-index material
                        (default ``None``)
    '''
    if isinstance(material, str):
        material = bpy.data.materials[material]
    if isinstance(material, int):
        material = game_object.blenderObject.material_slots[0].material
    (
        material
        .node_tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) += value


def get_world_socket(world, node, socket, output=False):
    '''Return the ``default_value`` of a socket in a world node tree.

    Reads the output socket when *output* is ``True``, otherwise reads the
    input socket.

    :param world: name string or ``World`` data-block
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param output: read from the output socket when ``True`` (default ``False``)

    :returns: current ``default_value`` of the socket
    '''
    if isinstance(world, str):
        world = bpy.data.worlds[world]
    return (
        world
        .node_tree
        .nodes[node]
        .outputs[socket]
        .default_value
    ) if output else (
        world
        .node_tree
        .nodes[node]
        .inputs[socket]
        .default_value
    )


def set_world_socket(world, node, socket, value, output=False):
    '''Set the ``default_value`` of a socket in a world node tree.

    When *output* is ``True``, the output socket is targeted instead of the
    input socket.

    :param world: name string or ``World`` data-block
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: new value to assign
    :param output: target the output socket when ``True`` (default ``False``)
    '''
    if isinstance(world, str):
        world = bpy.data.worlds[world]
    if output:
        (
            world
            .node_tree
            .nodes[node]
            .outputs[socket]
            .default_value
        ) = value
    else:
        (
            world
            .node_tree
            .nodes[node]
            .inputs[socket]
            .default_value
        ) = value


def modify_world_socket(world, node, socket, value, output=False):
    '''Add *value* to the ``default_value`` of a socket in a world node tree.

    When *output* is ``True``, the output socket is targeted instead of the
    input socket.

    :param world: name string or ``World`` data-block
    :param node: node name string or ``Node``
    :param socket: int index or ``NodeSocket``
    :param value: amount to add to the current socket value
    :param output: target the output socket when ``True`` (default ``False``)
    '''
    if isinstance(world, str):
        world = bpy.data.worlds[world]
    if output:
        (
            world
            .node_tree
            .nodes[node]
            .outputs[socket]
            .default_value
        ) = value
    else:
        (
            world
            .node_tree
            .nodes[node]
            .inputs[socket]
            .default_value
        ) += value

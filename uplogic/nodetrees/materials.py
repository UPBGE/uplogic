from bge.types import KX_GameObject as GameObject
from bpy.types import Material
from bpy.types import Node
from bpy.types import NodeSocket
import bpy


def get_material_socket(
    material: str or Material,
    node: Node,
    socket: NodeSocket,
    game_object: GameObject = None
):
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


def set_world_socket(world, node, socket, value, output=False):
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


def get_world_socket(world, node, socket, output=False):
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

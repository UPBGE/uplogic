from bge.types import KX_GameObject as GameObject
from bpy.types import NodeGroup
from bpy.types import Node
from bpy.types import NodeSocket
import bpy


def get_geom_socket(
    tree: str or NodeGroup,
    node: str or Node,
    socket: int or NodeSocket
):
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
    if isinstance(tree, str):
        tree = bpy.data.node_groups[tree]
    (
        tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) += value
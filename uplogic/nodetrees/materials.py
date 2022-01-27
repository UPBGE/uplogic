from bge.types import KX_GameObject as GameObject
from bpy.types import Material
from bpy.types import Node
from bpy.types import NodeSocket
import bpy


def get_material_socket(
    material: str or Material,
    node: Node,
    socket: NodeSocket,
    game_object=None
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


def set_material_socket(material, node, socket, value, game_object=None):
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

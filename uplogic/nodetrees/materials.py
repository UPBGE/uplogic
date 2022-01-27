import bpy


def get_material_socket(material, node, socket):
    return (
        bpy.data.materials[material]
        .node_tree
        .nodes[node]
        .inputs[socket]
        .default_value
    )


def set_material_socket(material, node, socket, value):
    (
        bpy.data.materials[material]
        .node_tree
        .nodes[node]
        .inputs[socket]
        .default_value
    ) = value

# from bge import render, logic
from bge.render import drawLine
from mathutils import Vector
from bge.types import KX_GameObject
from bpy.types import Mesh, MeshEdge


def draw_line(origin: Vector, target: Vector, color: list = [1, 1, 1, 1]):
    print('Moved from "uplogic.utils.visuals" to "uplogic.utils.visualize"!')
    drawLine(
        origin,
        target,
        color
    )


def draw_path(points: list, color: list = [1, 1, 1, 1]):
    print('Moved from "uplogic.utils.visuals" to "uplogic.utils.visualize"!')
    for i, p in enumerate(points):
        if i < len(points) - 1:
            drawLine(p, points[i+1], color)


def draw_cube(origin: Vector, width: float = 1, color: list = [1, 1, 1, 1], centered: bool = False):
    print('Moved from "uplogic.utils.visuals" to "uplogic.utils.visualize"!')
    draw_box(origin, width, width, width, color, centered)


def draw_box(origin: Vector, width: float, length: float, height: float, color: list = [1, 1, 1, 1], centered: bool = False):
    print('Moved from "uplogic.utils.visuals" to "uplogic.utils.visualize"!')
    if centered:
        origin = origin.copy() - Vector((width * .5, length * .5, height * .5))

    c1: Vector = origin.copy()
    c2: Vector = origin.copy()
    c3: Vector = origin.copy()
    c4: Vector = origin.copy()
    c5: Vector = origin.copy()
    c6: Vector = origin.copy()
    c7: Vector = origin.copy()

    c1[0] += length

    c2[0] += length
    c2[1] += width

    c3[1] += width

    c4[2] += height

    c5[0] += length
    c5[2] += height

    c6[0] += length
    c6[1] += width
    c6[2] += height

    c7[1] += width
    c7[2] += height

    drawLine(origin, c1, color)
    drawLine(c1, c2, color)
    drawLine(c2, c3, color)
    drawLine(c3, origin, color)

    drawLine(origin, c4, color)
    drawLine(c1, c5, color)
    drawLine(c2, c6, color)
    drawLine(c3, c7, color)

    drawLine(c4, c5, color)
    drawLine(c5, c6, color)
    drawLine(c6, c7, color)
    drawLine(c7, c4, color)


def draw_mesh(game_object: KX_GameObject, color: tuple = (1, 1, 1, 1)):
    print('Moved from "uplogic.utils.visuals" to "uplogic.utils.visualize"!')
    mesh: Mesh = game_object.blenderObject.data
    for edge in mesh.edges:
        v1 = mesh.vertices[edge.vertices[0]]
        v2 = mesh.vertices[edge.vertices[1]]
        drawLine(
            game_object.worldTransform @ Vector(v1.co),
            game_object.worldTransform @ Vector(v2.co),
            color
        )

from bge.render import drawLine
from bge import logic
from mathutils import Vector
from bge.types import KX_GameObject
from bpy.types import Mesh


def draw_line(origin: Vector, target: Vector, color: list = [1, 1, 1, 1]):
    drawLine(
        origin,
        target,
        color
    )


def draw_arrow(origin: Vector, target: Vector, color: list = [1, 1, 1, 1]):
    cam = logic.getCurrentScene().active_camera
    target = Vector(target)
    origin = Vector(origin)

    cam_dir = target - cam.worldPosition

    direction = target - origin
    normal = direction.cross(cam_dir).normalized() * direction.length

    drawLine(
        target,
        target - direction * .2 + normal * .1,
        color
    )

    drawLine(
        target,
        target - direction * .2 - normal * .1,
        color
    )

    drawLine(
        origin,
        target,
        color
    )


def draw_path(points: list, color: list = [1, 1, 1, 1]):
    for i, p in enumerate(points):
        if i < len(points) - 1:
            drawLine(p, points[i+1], color)


def draw_arrow_path(points: list, color: list = [1, 1, 1, 1]):
    for i, p in enumerate(points):
        if i < len(points) - 1:
            draw_arrow(p, points[i+1], color)



def draw_cube(origin: Vector, width: float = 1, color: list = [1, 1, 1, 1], centered: bool = False):
    draw_box(origin, width, width, width, color, centered)


def draw_box(origin: Vector, width: float, length: float, height: float, color: list = [1, 1, 1, 1], centered: bool = False):
    is_obj = isinstance(origin, KX_GameObject)

    if is_obj:
        obj = origin
        origin = origin.worldPosition.copy()
        origin -= obj.worldPosition
        centered = True
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

    if is_obj:
        ori = obj.worldOrientation
        offset = obj.worldPosition
        origin = ori @ origin + offset
        c1 = ori @ c1 + offset
        c2 = ori @ c2 + offset
        c3 = ori @ c3 + offset
        c4 = ori @ c4 + offset
        c5 = ori @ c5 + offset
        c6 = ori @ c6 + offset
        c7 = ori @ c7 + offset

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
    mesh: Mesh = game_object.blenderObject.data
    for edge in mesh.edges:
        v1 = mesh.vertices[edge.vertices[0]]
        v2 = mesh.vertices[edge.vertices[1]]
        drawLine(
            game_object.worldTransform @ Vector(v1.co),
            game_object.worldTransform @ Vector(v2.co),
            color
        )


def draw_axis(game_object: KX_GameObject, length=1.0):
    xaxis = game_object.getAxisVect((1, 0, 0)) * length
    yaxis = game_object.getAxisVect((0, 1, 0)) * length
    zaxis = game_object.getAxisVect((0, 0, 1)) * length
    wpos = game_object.worldPosition.copy()
    drawLine(wpos, wpos + xaxis, (1, 0, 0))  # +X
    drawLine(wpos, wpos + yaxis, (0, 1, 0))  # +Y
    drawLine(wpos, wpos + zaxis, (0, 0, 1))  # +Z
    drawLine(wpos, wpos - xaxis, (.5, 0, 0))  # -X
    drawLine(wpos, wpos - yaxis, (0, .5, 0))  # -Y
    drawLine(wpos, wpos - zaxis, (0, 0, .5))  # -Z

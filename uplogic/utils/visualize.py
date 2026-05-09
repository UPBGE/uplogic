'''Debug line-drawing helpers for uplogic, wrapping ``bge.render.drawLine``.
'''
from bge.render import drawLine
from bge import logic
from mathutils import Vector
from bge.types import KX_GameObject
from bpy.types import Mesh


def draw_line(origin: Vector, target: Vector, color: list = [1, 1, 1, 1]):
    '''Draw a single line segment from *origin* to *target*.

    :param origin: start point of the line as a ``Vector`` or sequence
    :param target: end point of the line as a ``Vector`` or sequence
    :param color: RGBA color as a 4-element list (default white ``[1, 1, 1, 1]``)
    '''
    drawLine(
        origin,
        target,
        color
    )


def draw_arrow(origin: Vector, target: Vector, color: list = [1, 1, 1, 1]):
    '''Draw a line from *origin* to *target* with two arrowhead lines at the
    target end, oriented toward the active camera.

    :param origin: start point of the arrow as a ``Vector`` or sequence
    :param target: tip of the arrow as a ``Vector`` or sequence
    :param color: RGBA color as a 4-element list (default white ``[1, 1, 1, 1]``)
    '''
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
    '''Draw a polyline through the list of *points*.

    Each consecutive pair of points is connected by a line segment.

    :param points: ordered list of positions (each a ``Vector`` or sequence)
    :param color: RGBA color as a 4-element list (default white ``[1, 1, 1, 1]``)
    '''
    for i, p in enumerate(points):
        if i < len(points) - 1:
            drawLine(p, points[i+1], color)


def draw_arrow_path(points: list, color: list = [1, 1, 1, 1]):
    '''Draw an arrowed polyline through *points*.

    Each segment of the path is drawn with an arrowhead at its end using
    ``draw_arrow``.

    :param points: ordered list of positions (each a ``Vector`` or sequence)
    :param color: RGBA color as a 4-element list (default white ``[1, 1, 1, 1]``)
    '''
    for i, p in enumerate(points):
        if i < len(points) - 1:
            draw_arrow(p, points[i+1], color)


def draw_cube(origin: Vector, width: float = 1, color: list = [1, 1, 1, 1], centered: bool = True):
    '''Draw a wireframe cube.

    When *centered* is ``True`` the cube is centred on *origin*. If *origin*
    is a ``KX_GameObject`` the cube is drawn in that object's local space.

    :param origin: centre or corner of the cube as a ``Vector``, sequence,
                   or ``KX_GameObject``
    :param width: side length of the cube (default ``1``)
    :param color: RGBA color as a 4-element list (default white ``[1, 1, 1, 1]``)
    :param centered: centre the cube on *origin* when ``True`` (default ``True``)
    '''
    draw_box(origin, width, width, width, color, centered)


def draw_box(origin: Vector, width: float, length: float, height: float, color: list = [1, 1, 1, 1], centered: bool = True):
    '''Draw a wireframe axis-aligned box.

    If *origin* is a ``KX_GameObject`` the box corners are transformed by the
    object's world orientation and position so the box aligns to the object's
    local axes.

    :param origin: corner or centre of the box as a ``Vector``, sequence,
                   or ``KX_GameObject``
    :param width: extent along the X axis
    :param length: extent along the Y axis
    :param height: extent along the Z axis
    :param color: RGBA color as a 4-element list (default white ``[1, 1, 1, 1]``)
    :param centered: centre the box on *origin* when ``True`` (default ``True``)
    '''
    is_obj = isinstance(origin, KX_GameObject)

    if is_obj:
        obj = origin
        origin = origin.worldPosition.copy()
        origin -= obj.worldPosition
        centered = True
    else:
        origin = Vector(origin)
    if centered:
        origin = origin.copy() - Vector((width * .5, length * .5, height * .5))

    c1: Vector = origin.copy()
    c2: Vector = origin.copy()
    c3: Vector = origin.copy()
    c4: Vector = origin.copy()
    c5: Vector = origin.copy()
    c6: Vector = origin.copy()
    c7: Vector = origin.copy()

    c1[0] += width

    c2[0] += width
    c2[1] += length

    c3[1] += length

    c4[2] += height

    c5[0] += width
    c5[2] += height

    c6[0] += width
    c6[1] += length
    c6[2] += height

    c7[1] += length
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
    '''Draw all mesh edges of *game_object*'s Blender mesh in world space.

    Each edge of the underlying ``Mesh`` data is transformed by the object's
    world transform before being drawn.

    :param game_object: ``KX_GameObject`` whose mesh edges will be drawn
    :param color: RGBA color as a 4-element tuple (default white ``(1, 1, 1, 1)``)
    '''
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
    '''Draw the three local axes of *game_object*.

    Positive halves are drawn at full brightness; negative halves are dimmed
    to half intensity.

    - X axis: red
    - Y axis: green
    - Z axis: blue

    :param game_object: ``KX_GameObject`` whose local axes will be visualised
    :param length: length of each axis line (default ``1.0``)
    '''
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

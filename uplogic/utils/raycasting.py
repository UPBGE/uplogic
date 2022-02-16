from bge import logic
from bge import render
from bge.types import KX_GameObject as GameObject
from mathutils import Vector


def ray_data(origin, dest, local, dist):
    """Get necessary data to calculate the ray.\n
    Not intended for manual use.
    """
    start = (
        origin.worldPosition.copy()
        if hasattr(origin, "worldPosition")
        else origin
    )
    if hasattr(dest, "worldPosition"):
        dest = dest.worldPosition.copy()
    if local:
        dest = start + dest
    d = dest - start
    d.normalize()
    return d, dist if dist else (start - dest).length, dest



def raycast(
    caster: GameObject,
    origin: Vector or GameObject,
    dest: Vector or GameObject,
    distance: float = 0,
    prop: str = '',
    xray: bool = False,
    local: bool = False,
    visualize: bool = False
) -> tuple[GameObject, Vector, Vector, Vector]:
    """Raycast from any point to any target

    :param `caster`: casting object, this object will be ignored by the ray.
    :param `origin`: origin point; any vector or list.
    :param `dest`: target point; any vector or list.
    :param `distance`: distance the ray will be cast
    (0 means the ray will only be cast to target).
    :param `prop`: look only for this property,
    leave empty to look for all.
    :param `xray`: look for objects behind others.
    :param `local`: add the target vector to the origin.
    :param `visualize`: show the raycast.

    :returns: `obj`, `point`, `normal`, `direction`
    """
    direction, distance, dest = ray_data(origin, dest, local, distance)
    obj, point, normal = caster.rayCast(
        dest,
        origin,
        distance,
        prop,
        xray=xray
    )
    if visualize:
        origin = getattr(origin, 'worldPosition', origin)
        line_dest: Vector = direction.copy()
        line_dest.x *= distance
        line_dest.y *= distance
        line_dest.z *= distance
        line_dest = line_dest + origin
        render.drawLine(
            origin,
            line_dest,
            [1, 0, 0, 1]
        )
        if obj:
            render.drawLine(
                origin,
                point,
                [0, 1, 0, 1]
            )
    return (obj, point, normal, direction)


def raycast_projectile(
    caster,
    origin,
    aim,
    power,
    distance=0,
    resolution=.9,
    prop='',
    xray=False,
    local=False,
    visualize=False
):
    def calc_projectile(self, t, vel, pos):
        half: float = logic.getCurrentScene().gravity.z * (.5 * t * t)
        vel = vel * t
        return Vector((0, 0, half)) + vel + pos

    aim.normalize()
    aim *= power
    origin = getattr(origin, 'worldPosition', origin)
    if local:
        origin = origin + caster.worldPosition

    points: list = []
    color: list = [1, 0, 0]
    idx = 0
    total_dist: float = 0

    while total_dist < distance:
        target = (calc_projectile(idx, aim, origin))
        start = origin if not points else points[-1]
        obj, point, normal = caster.rayCast(
            start,
            target,
            prop=prop,
            xray=xray
        )
        total_dist += (target-start).length
        if not obj:
            points.append(target)
        else:
            points.append(point)
            color = [0, 1, 0]
            break
        idx += resolution
    if visualize:
        for i, p in enumerate(points):
            if i < len(points) - 1:
                render.drawLine(p, points[i+1], color)
    return (obj, point, normal, points)


def raycast_camera(
    aim=(.5, .5),
    distance=0,
    prop='',
    xray=False
):
    # assume screen coordinates
    if isinstance(aim, Vector) and len(aim) == 2:
        vec = 10 * camera.getScreenVect(aim[0], aim[1])
        ray_target = camera.worldPosition - vec
        aim = ray_target
    if prop:
        obj, point, normal = camera.rayCast(
            aim,
            None,
            distance,
            prop,
            xray=xray
        )
    else:
        obj, point, normal = camera.rayCast(aim, None, distance)
    return (obj, point, normal)
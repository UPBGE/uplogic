'''Ray-casting helpers for uplogic. Provides ``raycast`` and specialised variants
for screen-space, projectile, and camera rays, plus the ``RayCastData`` result
tuple.
'''
from bge import logic
from bge import render
from bge.types import KX_GameObject as GameObject
from bge.types import KX_PolyProxy
from mathutils import Vector
from .math import clamp
from uplogic import console


def ray_data(
    origin: Vector,
    dest: Vector,
    local: bool,
    dist: float
):
    '''Get necessary data to calculate the ray.

    Not intended for manual use.

    Resolves ``worldPosition`` on both *origin* and *dest*, optionally adds
    *dest* as a local offset to *origin* when ``local=True``, normalises the
    direction vector, and extends *dest* to *dist* units along that direction.

    :param origin: ray start point; a ``Vector``, object with ``worldPosition``,
        or any sequence of three floats.
    :param dest: ray end point or local offset; same types as *origin*.
    :param local: when ``True``, treat *dest* as an offset relative to *origin*.
    :param dist: desired ray length; when ``0`` the distance between *origin*
        and *dest* is used instead.
    :returns: a 3-tuple ``(direction, dist, dest)`` where *direction* is the
        normalised direction ``Vector``, *dist* is the resolved ray length, and
        *dest* is the extended endpoint.
    '''
    origin = getattr(origin, 'worldPosition', origin)
    dest = getattr(dest, 'worldPosition', dest)
    if local:
        dest = origin + dest
    d = dest - origin
    d.normalize()
    dist = dist if dist else (origin - dest).length
    dest = origin + d * dist
    return d, dist, dest


class RayCastData(tuple):
    '''Typed tuple subclass returned by :func:`raycast` and its variants.

    Indices map to named properties for convenient attribute access.  When a ray
    misses, ``obj`` is ``None`` and the remaining fields are also ``None``.
    '''

    @property
    def obj(self) -> GameObject:
        '''Hit ``KX_GameObject``, or ``None`` when the ray misses.'''
        return self[0]

    @property
    def point(self) -> Vector:
        '''World-space ``Vector`` of the hit point, or ``None``.'''
        return self[1]

    @property
    def normal(self) -> Vector:
        '''Surface normal ``Vector`` at the hit point, or ``None``.'''
        return self[2]

    @property
    def direction(self) -> Vector:
        '''Normalised direction ``Vector`` of the ray.'''
        return self[3]

    @property
    def face(self) -> KX_PolyProxy:
        '''``KX_PolyProxy`` of the hit polygon when ``face_data=True``, otherwise ``None``.'''
        return self[4]

    @property
    def uv(self) -> Vector:
        '''UV coordinates at the hit point when ``face_data=True``, otherwise ``None``.'''
        return self[5]

# class RayCastDataPoly(RayCastData):



def raycast(
    caster: GameObject,
    origin: Vector,
    dest: Vector,
    distance: float = 0,
    prop: str = '',
    material: str = '',
    exclude: bool = None,
    xray: bool = False,
    local: bool = False,
    mask: int = 65535,
    face_data: bool = False,
    visualize: bool = False
) -> RayCastData[GameObject, Vector, Vector, Vector, KX_PolyProxy, Vector]:
    '''Raycast from any point to any target.

    When a ``material`` filter is active and ``xray=True``, the function
    continues casting from each successive hit point until it finds an object
    whose material matches *material* or the remaining distance runs out.

    :param caster: casting object; this object is ignored by the ray.
    :param origin: origin point; any ``Vector``, object with ``worldPosition``,
        or sequence of three floats.
    :param dest: target point; same types as *origin*.
    :param distance: distance the ray will be cast; ``0`` means the ray is cast
        only as far as *dest*.
    :param prop: restrict hits to objects that have this game property.
    :param material: restrict hits to objects that have this material applied.
    :param exclude: [DEPRECATED] formerly inverted the *prop* / *material*
        selection; passing any value logs a deprecation warning and has no
        further effect.
    :param xray: when ``True``, continue casting through objects that do not
        match the *prop* or *material* filter.
    :param local: when ``True``, treat *dest* as a local offset from *origin*.
    :param mask: collision mask for the ray.
    :param face_data: when ``True``, populate the ``face`` and ``uv`` fields of
        the returned :class:`RayCastData`.
    :param visualize: draw the ray in the viewport for debugging; green up to
        the hit point, red beyond.
    :returns: :class:`RayCastData` with fields
        ``(obj, point, normal, direction, face, uv)``.
    '''
    if exclude is not None:
        from ..console import warning
        warning("raycast parameter 'exclude' is deprecated and will be removed in future versions!")
        # exclude_prop, prop = prop, ''
    origin = getattr(origin, 'worldPosition', Vector(origin)).copy()
    dest = getattr(dest, 'worldPosition', Vector(dest)).copy()
    direction, distance, dest = ray_data(origin, dest, local, distance)
    ret_dat = [None, None, None, direction, None, None]
    data = caster.rayCast(
        dest,
        objfrom=origin,
        dist=distance,
        prop=prop,
        xray=xray,
        mask=mask,
        poly=2 if face_data else 0
    )
    obj, point = data[0], data[1]
    if (material and point):
        bo = obj.blenderObject
        leftover_dist = distance - (origin - point).length
        while (
            material not in [
                slot.material.name for
                slot in
                bo.material_slots
            ]
        ) and leftover_dist > 0:
            if not xray:
                data = [None, None, None, direction, None, None]
                break
            elif point:
                old_point = point
                data = obj.rayCast(
                    dest,
                    point,
                    leftover_dist,
                    prop,
                    xray=xray,
                    mask=mask,
                    poly=2 if face_data else 0
                )
                obj, point = data[0], data[1]
                if not obj:
                    break
                bo = obj.blenderObject
                leftover_dist -= (origin - old_point).length
            else:
                data = [None, None, None, direction, None, None]
                break
    ret_dat[0] = data[0]
    ret_dat[1] = data[1]
    ret_dat[2] = data[2]
    if face_data and len(data) > 3:
        ret_dat[4] = data[3]
        ret_dat[5] = data[4]
    data = RayCastData(ret_dat)
    if visualize:
        line_dest: Vector = direction.copy()
        line_dest.x *= distance
        line_dest.y *= distance
        line_dest.z *= distance
        line_dest = line_dest + origin
        if not data.obj:
            render.drawLine(
                origin,
                line_dest,
                [1, 0, 0, 1]
            )
        else:
            render.drawLine(
                origin,
                point,
                [0, 1, 0, 1]
            )
            render.drawLine(
                point,
                line_dest,
                [1, 0, 0, 1]
            )
    return data


class RayCastFaceData(RayCastData):
    '''[DEPRECATED] Use :func:`raycast` with ``face_data=True`` instead.'''
    pass


def raycast_face(
    caster: GameObject,
    origin: Vector,
    dest: Vector,
    distance: float = 0,
    prop: str = '',
    material: str = '',
    exclude: bool = False,
    xray: bool = False,
    local: bool = False,
    mask: int = 65535,
    face_data: bool = False,
    visualize: bool = False
) -> RayCastFaceData[GameObject, Vector, Vector, Vector, KX_PolyProxy, Vector]:
    '''[DEPRECATED] Raycast from any point to any target with face data.

    .. deprecated::
        Use :func:`raycast` with ``face_data=True`` instead.  This function
        logs a deprecation warning and returns an empty
        :class:`RayCastFaceData` tuple.

    :param caster: casting object; this object is ignored by the ray.
    :param origin: origin point; any ``Vector``, object with ``worldPosition``,
        or sequence of three floats.
    :param dest: target point; same types as *origin*.
    :param distance: distance the ray will be cast; ``0`` means the ray is cast
        only as far as *dest*.
    :param prop: restrict hits to objects that have this game property.
    :param material: restrict hits to objects that have this material applied.
    :param exclude: invert the selection for *prop* and *material*.
    :param xray: when ``True``, continue casting through non-matching objects.
    :param local: when ``True``, treat *dest* as a local offset from *origin*.
    :param mask: collision mask for the ray.
    :param face_data: unused; kept for API compatibility.
    :param visualize: unused; kept for API compatibility.
    :returns: :class:`RayCastFaceData` with all fields set to ``None``.
    '''
    console.warning("'uplogic.utils.raycasting.raycast_face()' is deprecated, use '...raycasting.raycast(face_data=True)' instead")
    return RayCastFaceData((None, None, None, None, None, None))


class RayCastDataProjectile(RayCastData):
    '''Typed tuple subclass returned by :func:`raycast_projectile`.

    Extends :class:`RayCastData` with a ``points`` property containing the
    waypoints along the computed parabola, and overrides ``direction`` to
    return the direction of the last parabolic segment rather than the initial
    ray direction.
    '''

    @property
    def points(self) -> list[Vector]:
        '''List of ``Vector`` waypoints along the parabolic trajectory.'''
        return self[3]

    @property
    def direction(self) -> Vector:
        '''Normalised direction of the last parabolic segment.

        Returns a zero ``Vector`` when fewer than two points are available.
        '''
        p = self.points
        if len(p) > 1:
            return (p[-1] - p[-2]).normalized()
        else:
            return Vector((0, 0, 0))


def raycast_projectile(
    caster: GameObject,
    origin: Vector,
    aim: Vector,
    power: float,
    distance: float = 100,
    resolution: float = .05,
    prop: str = '',
    material: str = '',
    xray: bool = False,
    local: bool = False,
    mask: int = 65535,
    gravity: Vector = None,
    face_data: bool = False,
    visualize: bool = False
) -> RayCastDataProjectile[GameObject, Vector, Vector, Vector, KX_PolyProxy, Vector, list]:
    '''Raycast along the predicted parabola of a projectile.

    Uses ballistic motion (the inner ``calc_projectile`` function) to step
    along the arc in *resolution* increments until a hit is detected or
    *distance* is exhausted.  When *gravity* is ``None``, the current scene
    gravity is used.

    :param caster: casting object; this object is ignored by the ray.
    :param origin: origin point; any ``Vector`` or object with
        ``worldPosition``.
    :param aim: initial aim direction; the parabola starts towards this point.
    :param power: initial speed of the projectile; higher values produce
        longer, flatter arcs.
    :param distance: total arc length at which casting stops.
    :param resolution: step size along the arc; lower values give finer detail.
        Clamped to ``[0.01, 0.99]``.
    :param prop: restrict hits to objects that have this game property.
    :param material: restrict hits to objects that have this material applied.
    :param xray: when ``True``, continue casting through non-matching objects.
    :param local: when ``True``, treat *aim* as a local offset from *origin*.
    :param mask: collision mask for the ray.
    :param gravity: custom gravity ``Vector``; when ``None`` the scene gravity
        is used.
    :param face_data: when ``True``, populate the ``face`` and ``uv`` fields of
        the returned :class:`RayCastDataProjectile`.
    :param visualize: draw the arc segments in the viewport for debugging.
    :returns: :class:`RayCastDataProjectile` with fields
        ``(obj, point, normal, points, face, uv)``.
    '''
    def calc_projectile(t, vel, pos, gravity):
        half: float = gravity * (.5 * t * t)
        vel = vel * t
        return half + vel + pos

    if not local:
        aim = aim - origin
    aim.normalize()
    aim *= power
    origin = getattr(origin, 'worldPosition', origin)

    points: list = [origin]
    color: list = [1, 0, 0]
    idx = 0
    total_dist: float = 0
    resolution = clamp(resolution, .01, .99)

    grav = gravity if gravity else logic.getCurrentScene().gravity
    while total_dist < distance:
        target = (calc_projectile(idx, aim, origin, grav))
        start = origin if not points else points[-1]
        data = raycast(
            caster=caster,
            origin=start,
            dest=target,
            prop=prop,
            material=material,
            xray=xray,
            local=False,
            mask=mask,
            face_data=face_data,
            visualize=False
        )
        total_dist += (target-start).length
        if not data.obj:
            points.append(target)
        else:
            points.append(data.point)
            color = [0, 1, 0]
            break
        idx += resolution
    if visualize:
        for i, p in enumerate(points):
            if i < len(points) - 1:
                render.drawLine(p, points[i+1], color)
    return RayCastDataProjectile((data.obj, data.point, data.normal, points, data.face, data.uv))


class RayCastCameraData(tuple):
    '''Minimal ray hit tuple returned by :func:`raycast_camera`.

    Contains only ``obj``, ``point``, and ``normal``; prefer
    :class:`RayCastData` from :func:`raycast_screen` for new code.
    '''

    @property
    def obj(self) -> GameObject:
        '''Hit ``KX_GameObject``, or ``None`` when the ray misses.'''
        return self[0]

    @property
    def point(self) -> Vector:
        '''World-space ``Vector`` of the hit point, or ``None``.'''
        return self[1]

    @property
    def normal(self) -> Vector:
        '''Surface normal ``Vector`` at the hit point, or ``None``.'''
        return self[2]


def raycast_camera(
    distance: float = 0,
    prop: str = '',
    xray: bool = False,
    aim: Vector = Vector((.5, .5)),
    mask: int = 65535
) -> RayCastCameraData:
    '''[DEPRECATED] Cast a ray from the active camera through screen coordinates.

    .. deprecated::
        Use :func:`raycast_screen` instead.  This function logs a deprecation
        warning and delegates to the BGE camera ``rayCast`` method directly.

    :param distance: distance the ray will be cast.
    :param prop: restrict hits to objects that have this game property.
    :param xray: when ``True``, continue casting through non-matching objects.
    :param aim: X and Y screen coordinates in the range ``0``–``1``; defaults
        to the centre of the screen.
    :param mask: collision mask for the ray.
    :returns: :class:`RayCastCameraData` with fields ``(obj, point, normal)``.
    '''
    # assume screen coordinates
    from ..console import warning
    warning("'raycasting.raycast_camera' is deprecated and will be removed in future versions, please use 'raycasting.raycast_screen' instead!")
    camera = logic.getCurrentScene().active_camera
    if isinstance(aim, Vector) and len(aim) == 2:
        vec = 10 * camera.getScreenVect(aim[0], aim[1])
        ray_target = camera.worldPosition - vec
        aim = ray_target
    obj, point, normal = camera.rayCast(
        aim,
        None,
        distance,
        prop,
        xray=xray,
        mask=mask
    )
    return RayCastCameraData((obj, point, normal))


def raycast_screen(
    caster=None,
    aim: Vector = None,
    distance: float = 100,
    prop: str = '',
    material: str = '',
    xray: bool = False,
    mask: int = 65535,
    face_data: bool = False

) -> RayCastData[GameObject, Vector, Vector, Vector, KX_PolyProxy, Vector]:
    '''Cast a ray from the active camera through 2-D screen coordinates.

    Converts the *aim* screen coordinates (in the range ``0``–``1``) to a
    world-space direction using the active camera's ``getScreenVect`` method,
    then delegates to :func:`raycast`.  When *aim* is ``None``, the current
    mouse position is used.

    :param caster: casting object; defaults to the active camera when ``None``.
    :param aim: 2-D screen coordinates as a ``Vector`` or sequence ``(x, y)``
        in the range ``0``–``1``; when ``None`` the current mouse position is
        used.
    :param distance: distance the ray will be cast.
    :param prop: restrict hits to objects that have this game property.
    :param material: restrict hits to objects that have this material applied.
    :param xray: when ``True``, ignore objects that lack the required *material*
        or *prop* and continue casting.
    :param mask: collision mask for the ray.
    :param face_data: when ``True``, populate the ``face`` and ``uv`` fields of
        the returned :class:`RayCastData`.
    :returns: :class:`RayCastData` with fields
        ``(obj, point, normal, direction, face, uv)``.
    '''
    # assume screen coordinates
    camera = logic.getCurrentScene().active_camera
    # if aim is not None:
    #     aim = Vector(aim)
    if aim is not None and len(aim) == 2:
        vec = 10 * camera.getScreenVect(aim[0], aim[1])
    else:
        mpos = logic.mouse.position
        vec = 10 * camera.getScreenVect(*mpos)
    ray_target = camera.worldPosition - vec
    aim = ray_target
    data = raycast(
        caster=caster if caster is not None else camera,
        dest=aim,
        origin=camera.worldPosition,
        distance=distance,
        material=material,
        prop=prop,
        xray=xray,
        mask=mask,
        face_data=face_data
    )
    return RayCastData(data)


def raycast_mouse(
    distance: float = 100,
    prop: str = '',
    material: str = '',
    exclude: bool = False,
    xray: bool = False,
    mask: int = 65535
) -> RayCastData:
    '''[DEPRECATED] Cast a ray from the active camera to the world cursor.

    .. deprecated::
        Use :func:`raycast_screen` instead.  This function logs a deprecation
        warning and then calls :func:`raycast` directly with the mouse position
        converted to a world-space ray target.

    :param distance: distance the ray will be cast.
    :param prop: restrict hits to objects that have this game property.
    :param material: restrict hits to objects that have this material applied.
    :param exclude: invert the selection for *prop* and *material*.
    :param xray: when ``True``, continue casting through non-matching objects.
    :param mask: collision mask for the ray.
    :returns: :class:`RayCastData` with fields
        ``(obj, point, normal, direction, None, None)``.
    '''
    from ..console import warning
    warning("'raycasting.raycast_camera' is deprecated and will be removed in future versions, please use 'raycasting.raycast_screen' instead!")
    camera = logic.getCurrentScene().active_camera
    mpos = logic.mouse.position
    vec = 10 * camera.getScreenVect(*mpos)
    ray_target = camera.worldPosition - vec
    return raycast(
        camera,
        camera.worldPosition,
        ray_target,
        distance,
        prop,
        material,
        exclude,
        xray,
        mask=mask
    )

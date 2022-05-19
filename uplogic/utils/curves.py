from bge import logic
from bge.types import KX_GameObject as GameObject
import bpy
from bpy.types import Material


def create_curve(
    name: str,
    bevel_depth: float = 0.0,
    dimensions: int = 3,
    material: str or Material = None,
    collection: str = None
) -> GameObject:
    """Create a `KX_GameObject` containing a `bpy.types.Curve` object.

    :param `name`: Name of the new `KX_GameObject`.
    :param `bevel_depth`: Define the "thickness" of the curve. This will add
    geometry along the spline.
    :param `dimensions`: Set the coordinate space in which to calculate the
    curve.
    :param `material`: The material to use for bevel geometry.
    :param `collection`: The collection to which to add the curve. Leave at
    `None` to use scene collection.
    """
    bcurve = bpy.data.curves.new(name, 'CURVE')
    bcurve.bevel_depth = bevel_depth
    bcurve.dimensions = f'{dimensions}D'
    bobj = bpy.data.objects.new(name, bcurve)
    if material:
        if isinstance(material, str):
            bobj.data.materials.append(bpy.data.materials[material])
        elif isinstance(material, Material):
            bobj.data.materials.append(material)
    if collection:
        if isinstance(collection, str):
            collection = bpy.data.collections.get(collection, bpy.context.scene.collection)
    elif collection is None:
        collection = bpy.context.scene.collection
    collection.objects.link(bobj)
    game_obj = logic.getCurrentScene().convertBlenderObject(bobj)
    return game_obj


def set_curve_points(
    curve: GameObject,
    points: list
) -> None:
    """Set the curve points of a `KX_GameObject` containing a `bpy.types.Curve` object.

    :param `curve`: `KX_GameObject`
    :param `points`: A list of points to use for the curve.
    """
    bcurve = curve.blenderObject.data
    for spline in bcurve.splines:
        bcurve.splines.remove(spline)
    spline = bcurve.splines.new('POLY')
    pos = curve.worldPosition

    spline.points.add(len(points)-1)
    for p, new_co in zip(spline.points, points):
        p.co = ([
            new_co[0] - pos.x,
            new_co[1] - pos.y,
            new_co[2] - pos.z
        ] + [1.0])


class ULCurve():
    """Wrapper class for creating and handling curves more easily.

    :param `name`: Name of this curve object.
    :param `bevel_depth`: Define the "thickness" of the curve. This will add
    geometry along the spline.
    :param `dimensions`: Set the coordinate space in which to calculate the
    curve.
    :param `material`: The material to use for bevel geometry.
    :param `collection`: The collection to which to add the curve. Leave at
    `None` to use scene collection.
    """

    def __init__(
        self,
        name: str,
        bevel_depth: float = 0.0,
        dimensions: int = 3,
        material: str or Material =None,
        collection: str = None
    ) -> None:
        self.object = create_curve(
            name,
            bevel_depth,
            dimensions,
            material,
            collection
        )

    @property
    def name(self):
        """Name of the game object (Read-Only)."""
        return self.object.name

    @name.setter
    def name(self, val):
        print('ULCurve.name is read-only!')

    @property
    def points(self):
        """Points of the curve. These points use global coordinates."""
        splines = self.object.blenderObject.data.splines
        return splines[0].points if len(splines) > 0 else []

    @points.setter
    def points(self, val):
        if val != self.points:
            set_curve_points(self.object, val)

    @property
    def bevel_depth(self):
        """Thickness of the curve geometry."""
        return self.object.blenderObject.data.bevel_depth

    @bevel_depth.setter
    def bevel_depth(self, val):
        self.object.blenderObject.data.bevel_depth = val
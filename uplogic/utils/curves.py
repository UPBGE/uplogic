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
    """Set the curve points of a `KX_GameObject` containing a `bpy.types.Curve` object.
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
    def points(self):
        splines = self.object.blenderObject.data.splines
        return splines[0].points if len(splines) > 0 else []

    @points.setter
    def points(self, val):
        if val != self.points:
            set_curve_points(self.object, val)

    @property
    def bevel_depth(self):
        return self.object.blenderObject.data.bevel_depth

    @bevel_depth.setter
    def bevel_depth(self, val):
        self.object.blenderObject.data.bevel_depth = val
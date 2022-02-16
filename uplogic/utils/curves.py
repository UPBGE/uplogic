def set_curve_points(curve, points):
    bcurve = curve.blenderObject.data
    for spline in bcurve.splines:
        bcurve.splines.remove(spline)
    spline = bcurve.splines.new('NURBS')
    pos = curve.worldPosition
    spline.points.add(len(points))
    for p, new_co in zip(spline.points, points):
        p.co = ([
            new_co[0] - pos.x,
            new_co[1] - pos.y,
            new_co[2] - pos.z
        ] + [1.0])

from build123d import *

width = 70.0
depth = 30.0
thickness = 5.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_depth_cut = 2.0
hole_diameter = 3.0
countersink_diameter = 5.0
countersink_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.5

base = Box(width, depth, thickness)
pocket = Pos(0, 0, thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
result = base - pocket

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, thickness, countersink_angle)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")
from build123d import *

base_length = 80.0
base_width = 40.0
base_thickness = 4.0
flange_width = 8.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
chamfer_size = 0.3

base = Box(base_length, base_width, base_thickness)
flange = Pos(0, base_width/2 + flange_width/2, 0) * Box(base_length, flange_width, base_thickness)
result = base + flange

pocket = Pos(0, 0, base_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, base_thickness * 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_flange"
export_step(part, "output.step")
from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
flange_width = 8.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
fillet_radius = 0.5

base = Box(plate_length, plate_width, plate_thickness)
flange = Pos(0, plate_width/2 + flange_width/2, 0) * Box(plate_length, flange_width, plate_thickness)
result = base + flange

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_flange_pocket_and_holes"
export_step(part, "output.step")
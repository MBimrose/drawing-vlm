from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
flange_height = 8.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
relief_radius = 3.0
chamfer_size = 0.5
fillet_radius = 0.5

base_plate = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
flange = Pos(0, plate_width/2 + flange_height/2, plate_thickness/2) * Box(plate_length, flange_height, plate_thickness)
result = base_plate + flange

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

relief = Pos(plate_length/2 - relief_radius, 0, plate_thickness/2) * Cylinder(relief_radius, plate_thickness + 1)
result = result - relief

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_flange_pocket_holes"
export_step(part, "output.step")
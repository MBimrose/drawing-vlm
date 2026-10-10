from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 20.0
cyl_radius = 25.0
cyl_height = 20.0
wall_thickness = 1.5
fillet_radius = 2.7
hole_diameter = 12.0
hole_spacing = 40.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 5.0

base_plate = Box(plate_length, plate_width, plate_thickness)
cyl = Cylinder(cyl_radius, cyl_height)
solid_body = base_plate + cyl

solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + cyl_height + 10)

pocket = Pos(0, 0, plate_thickness + cyl_height - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "plate_with_cylinder"
export_step(part, "output.step")
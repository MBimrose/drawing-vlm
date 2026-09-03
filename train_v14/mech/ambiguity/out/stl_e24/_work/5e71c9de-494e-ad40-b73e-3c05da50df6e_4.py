from build123d import *

plate_width = 80.0
plate_depth = 50.0
plate_thickness = 8.0
corner_fillet = 3.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 24.0
recess_diameter = 30.0
recess_depth = 2.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)

part = solid_body
part.name = "plate_with_holes_and_recess"
export_step(part, "output.step")
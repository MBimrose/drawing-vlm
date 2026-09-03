from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 40.0
pocket_width = 30.0
hole_diameter = 4.0
hole_depth = plate_thickness - 2.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
fillet_radius = 2.0
chamfer_distance = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = chamfer(solid_body.edges(), chamfer_distance)

pocket = Box(pocket_length, pocket_width, plate_thickness)
solid_body = solid_body - pocket

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y),
    (0, -hole_spacing_y),
    (hole_spacing_x, -hole_spacing_y),
    (-hole_spacing_x, hole_spacing_y),
    (0, hole_spacing_y),
    (hole_spacing_x, hole_spacing_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")
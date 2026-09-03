from build123d import *

overall_length = 80.0
overall_width = 40.0
thickness = 10.0
central_bore_diameter = 25.4
hole_diameter = 6.3
hole_counterbore_diameter = 12.7
hole_counterbore_depth = 4.0
hole_spacing_x = 40.0
hole_spacing_y = 20.0
chamfer_distance = 1.0

solid_body = Box(overall_length, overall_width, thickness)
solid_body = solid_body - Cylinder(central_bore_diameter / 2, thickness)

for x in [-hole_spacing_x / 2, hole_spacing_x / 2]:
    for y in [-hole_spacing_y / 2, hole_spacing_y / 2]:
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness)
        solid_body = solid_body - Pos(x, y, thickness / 2 - hole_counterbore_depth / 2) * Cylinder(hole_counterbore_diameter / 2, hole_counterbore_depth)

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_bore_and_counterbored_holes"
export_step(part, "output.step")
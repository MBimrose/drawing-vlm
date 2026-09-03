from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 5.0
step_height = 8.0
step_width = 20.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
fillet_radius = 2.0

base = Box(leaf_length, leaf_width, leaf_thickness)
step = Pos(leaf_length/2 - step_width/2, 0, leaf_thickness/2 + step_height/2) * Box(step_width, leaf_width, step_height)
solid_body = base + step

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y/2),
    (0, -hole_spacing_y/2),
    (hole_spacing_x, -hole_spacing_y/2),
    (-hole_spacing_x, hole_spacing_y/2),
    (0, hole_spacing_y/2),
    (hole_spacing_x, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "leaf_with_step_and_holes"
export_step(part, "output.step")
from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 5.0
shoulder_length = 20.0
shoulder_height = 8.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
fillet_radius = 2.0

base = Box(bracket_length, bracket_width, bracket_thickness)
shoulder = Pos(bracket_length/2 - shoulder_length/2, 0, bracket_thickness/2 + shoulder_height/2) * Box(shoulder_length, bracket_width, shoulder_height)
solid_body = base + shoulder

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
part.name = "bracket"
export_step(part, "output.step")
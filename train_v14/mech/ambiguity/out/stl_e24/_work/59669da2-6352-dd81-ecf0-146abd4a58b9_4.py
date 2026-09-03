from build123d import *

bracket_length = 80
bracket_width = 30
bracket_thickness = 6
shoulder_length = 20
shoulder_height = 12
hole_diameter = 5
hole_spacing_x = 20
hole_spacing_y = 10
fillet_radius = 2

base = Box(bracket_length, bracket_width, bracket_thickness)
shoulder = Pos(bracket_length/2 - shoulder_length/2, 0, bracket_thickness) * Box(shoulder_length, bracket_width, shoulder_height)
combined = base + shoulder

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y/2),
    (0, -hole_spacing_y/2),
    (hole_spacing_x, -hole_spacing_y/2),
    (-hole_spacing_x, hole_spacing_y/2),
    (0, hole_spacing_y/2),
    (hole_spacing_x, hole_spacing_y/2),
]

for x, y in hole_positions:
    combined = combined - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness + shoulder_height + 10)

combined = fillet(combined.edges(), fillet_radius)

part = combined
part.name = "bracket"
export_step(part, "output.step")
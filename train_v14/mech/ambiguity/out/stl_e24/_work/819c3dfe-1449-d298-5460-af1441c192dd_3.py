from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
hole_diameter = 4.0
hole_spacing = 40.0

part = Box(bracket_length, bracket_width, bracket_thickness)
for x in [-hole_spacing/2, hole_spacing/2]:
    part = part - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness)

part.name = "bracket"
export_step(part, "output.step")
from build123d import *

bracket_length = 70
bracket_width = 30
bracket_thickness = 8
hole_diameter = 4
hole_spacing = 40

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")
from build123d import *

bracket_length = 70
bracket_width = 30
bracket_thickness = 8
hole_diameter = 4
hole_spacing = 40

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid = p.part
for x in [-hole_spacing/2, hole_spacing/2]:
    solid = solid - Pos(x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

part = solid
part.name = "bracket"
export_step(part, "output.step")
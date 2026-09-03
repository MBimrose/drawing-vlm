from build123d import *

bracket_length = 80.0
bracket_width = 60.0
bracket_thickness = 8.0
rib_height = 12.0
rib_width = 6.0
rib_thickness = 3.0
rib_offset = 10.0
hole_diameter = 16.0
hole_offset = 10.0
chamfer_distance = 1.5

base = Box(bracket_length, bracket_width, bracket_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

hole_positions = [
    (-bracket_length/2 + hole_offset, -bracket_width/2 + hole_offset),
    ( bracket_length/2 - hole_offset,  bracket_width/2 - hole_offset)
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness + 2)

rib_positions = [
    (-bracket_length/2 + rib_offset, -bracket_width/2 + rib_offset),
    ( bracket_length/2 - rib_offset, -bracket_width/2 + rib_offset),
    (-bracket_length/2 + rib_offset,  bracket_width/2 - rib_offset),
    ( bracket_length/2 - rib_offset,  bracket_width/2 - rib_offset)
]
for x, y in rib_positions:
    base = base + Pos(x, y, bracket_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

part = base
part.name = "bracket_with_ribs"
export_step(part, "output.step")
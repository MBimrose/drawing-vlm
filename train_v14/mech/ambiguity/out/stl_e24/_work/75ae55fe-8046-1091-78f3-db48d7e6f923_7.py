from build123d import *

bracket_width = 80.0
bracket_height = 25.0
bracket_thickness = 8.0
cutout_width = 30.0
cutout_height = 15.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 8.0
rib_width = 4.0
rib_height = 12.0
rib_thickness = 3.0
rib_spacing = 10.0

result = Box(bracket_width, bracket_thickness, bracket_height)

cutout = Pos(0, 0, -bracket_height/2 + cutout_height/2) * Box(cutout_width, bracket_thickness, cutout_height)
result = result - cutout

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (-bracket_width/2 + hole_offset, -bracket_height/2 + hole_offset),
    (bracket_width/2 - hole_offset, -bracket_height/2 + hole_offset),
    (-bracket_width/2 + hole_offset, bracket_height/2 - hole_offset),
    (bracket_width/2 - hole_offset, bracket_height/2 - hole_offset),
]
for x, z in hole_positions:
    hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)
    result = result - hole

num_ribs = int((bracket_width - 2*hole_offset) // rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -bracket_width/2 + hole_offset + i * rib_spacing
    rib = Pos(x_pos, bracket_thickness/2 + rib_thickness/2, rib_height/2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

part = result
part.name = "bracket_with_cutout_and_ribs"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 30.0
outer_height = 60.0
wall_thickness = 1.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 3
hole_offset_from_end = 12.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, wall_thickness + rib_height / 2) * Box(rib_thickness, outer_width - 2 * wall_thickness, rib_height)
result = base + rib

for i in range(hole_count):
    x = -outer_length / 2 + hole_offset_from_end + i * hole_spacing
    result = result - Pos(x, 0, outer_height / 2) * Cylinder(hole_diameter / 2, outer_height)

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "hollow_box_with_rib"
export_step(part, "output.step")
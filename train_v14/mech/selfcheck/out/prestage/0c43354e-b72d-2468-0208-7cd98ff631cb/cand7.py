from build123d import *

outer_width = 80.0
outer_height = 30.0
length = 60.0
wall_thickness = 1.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_edge = 12.0
num_holes = 3

base = Box(outer_width, outer_height, length)
bottom_face = base.faces().sort_by(Axis.Z)[0]
hollow = offset(base, amount=-wall_thickness, openings=[bottom_face])

rib = Box(rib_thickness, outer_height - 2*wall_thickness, length)
combined = hollow + rib

start_x = -outer_width/2 + hole_offset_from_edge
for i in range(num_holes):
    x = start_x + i * hole_spacing
    combined = combined - Pos(x, 0, 0) * Cylinder(hole_diameter/2, length)

part = combined
part.name = "hollow_box_with_rib_and_holes"
export_step(part, "output.step")
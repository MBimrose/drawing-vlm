from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_spacing = 20.0
rib_count = 3
slot_width = 5.0
slot_height = outer_height - 2 * wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
result = offset(base, amount=-wall_thickness, openings=[top_face])

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
for i in range(rib_count):
    x_pos = -inner_length/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness + rib_height/2) * Box(rib_thickness, inner_width, rib_height)
    result = result + rib

slot = Pos(0, -outer_width/2 + wall_thickness/2, outer_height/2 - slot_height/2) * Box(slot_width, wall_thickness, slot_height)
result = result - slot

part = result
part.name = "shelled_box_with_ribs_and_slot"
export_step(part, "output.step")
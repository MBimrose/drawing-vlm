from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_spacing = (outer_length - 2 * wall_thickness) / 4
slot_width = 5.0
slot_height = 15.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib1 = Pos(-outer_length / 2 + wall_thickness + rib_spacing, 0, rib_height / 2) * Box(rib_thickness, outer_width - 2 * wall_thickness, rib_height)
rib2 = Pos(0, 0, rib_height / 2) * Box(rib_thickness, outer_width - 2 * wall_thickness, rib_height)
rib3 = Pos(outer_length / 2 - wall_thickness - rib_spacing, 0, rib_height / 2) * Box(rib_thickness, outer_width - 2 * wall_thickness, rib_height)

result = base + rib1 + rib2 + rib3

slot_cut = Pos(0, -outer_width / 2 + wall_thickness / 2, outer_height / 2 - slot_height / 2) * Box(slot_width, wall_thickness, slot_height)
result = result - slot_cut

front_face = result.faces().sort_by(Axis.Y)[0]
front_edges = front_face.edges().filter_by(Axis.Z)
result = chamfer(front_edges, chamfer_size)

part = result
part.name = "hollow_box_with_ribs_and_slot"
export_step(part, "output.step")
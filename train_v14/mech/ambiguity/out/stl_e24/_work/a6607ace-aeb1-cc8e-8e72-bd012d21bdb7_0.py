from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 12.0
vent_slot_height = 5.0
vent_slot_spacing = 15.0
rib_thickness = 1.0
rib_height = 6.0
rib_spacing = 8.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_slot = Box(wall_thickness, vent_slot_width, vent_slot_height)
for z_off in [-vent_slot_spacing/2, vent_slot_spacing/2]:
    solid_body = solid_body - Pos(outer_length/2 - wall_thickness/2, 0, outer_height/2 + z_off) * vent_slot
    solid_body = solid_body - Pos(-outer_length/2 + wall_thickness/2, 0, outer_height/2 + z_off) * vent_slot

rib_slot = Box(wall_thickness, rib_thickness, rib_height)
num_ribs = int((outer_length - 2*wall_thickness) // rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -outer_length/2 + wall_thickness + i * rib_spacing
    solid_body = solid_body - Pos(x_pos, outer_width/2 - wall_thickness/2, wall_thickness + rib_height/2) * rib_slot
    solid_body = solid_body - Pos(x_pos, -outer_width/2 + wall_thickness/2, wall_thickness + rib_height/2) * rib_slot

part = solid_body
part.name = "vented_box_with_ribs"
export_step(part, "output.step")
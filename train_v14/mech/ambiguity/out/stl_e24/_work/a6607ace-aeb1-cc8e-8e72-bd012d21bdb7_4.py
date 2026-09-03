from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 8.0
rib_spacing = 10.0
vent_slot_width = 12.0
vent_slot_height = 5.0
vent_slot_spacing = 12.0
vent_slot_count = 2
vent_slot_offset_from_bottom = 10.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

rib_count = int((outer_length - 2 * wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -outer_length/2 + wall_thickness + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
    solid_body = solid_body + rib

for i in range(vent_slot_count):
    z_pos = vent_slot_offset_from_bottom + i * vent_slot_spacing
    vent = Pos(outer_length/2 - wall_thickness/2, 0, z_pos) * Box(wall_thickness, vent_slot_width, vent_slot_height)
    solid_body = solid_body - vent

for i in range(vent_slot_count):
    z_pos = vent_slot_offset_from_bottom + i * vent_slot_spacing
    vent = Pos(-outer_length/2 + wall_thickness/2, 0, z_pos) * Box(wall_thickness, vent_slot_width, vent_slot_height)
    solid_body = solid_body - vent

hole_positions = [
    (outer_length/2 - mount_hole_offset, outer_width/2 - mount_hole_offset),
    (-outer_length/2 + mount_hole_offset, outer_width/2 - mount_hole_offset),
    (outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "vented_box_with_ribs"
export_step(part, "output.step")
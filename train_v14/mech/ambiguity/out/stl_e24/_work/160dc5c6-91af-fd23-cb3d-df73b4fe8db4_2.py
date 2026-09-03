from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_length = 50.0
vent_slot_height = 10.0
vent_slot_offset_from_top = 5.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_center_z = outer_height/2 - vent_slot_offset_from_top - vent_slot_height/2
vent_cut = Pos(0, -outer_width/2 + wall_thickness/2, vent_center_z) * Box(vent_slot_length, wall_thickness, vent_slot_height)
solid_body = solid_body - vent_cut

px = outer_length/2 - mount_hole_offset
py = outer_width/2 - mount_hole_offset
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

part = solid_body
part.name = "vented_enclosure"
export_step(part, "output.step")
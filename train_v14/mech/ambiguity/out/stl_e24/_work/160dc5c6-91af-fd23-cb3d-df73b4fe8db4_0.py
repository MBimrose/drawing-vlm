from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
vent_slot_width = 50.0
vent_slot_height = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_cut = Pos(0, -enclosure_width/2 + wall_thickness/2, enclosure_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
solid_body = solid_body - vent_cut

hole_r = mount_hole_diameter / 2
hole_h = enclosure_height + 10
for x in [-enclosure_length/2 + mount_hole_offset, enclosure_length/2 - mount_hole_offset]:
    for y in [-enclosure_width/2 + mount_hole_offset, enclosure_width/2 - mount_hole_offset]:
        solid_body = solid_body - Pos(x, y, enclosure_height/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "enclosure_with_vent_and_mount_holes"
export_step(part, "output.step")
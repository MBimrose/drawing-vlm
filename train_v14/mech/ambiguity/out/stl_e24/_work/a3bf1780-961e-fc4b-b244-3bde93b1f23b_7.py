from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
vent_slot_width = 30.0
vent_slot_height = 10.0
vent_offset_from_top = 5.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
rib_width = 6.0
rib_height = 10.0
rib_thickness = 1.0

solid_body = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

base_plate = Pos(0, 0, base_thickness/2) * Box(enclosure_length - 2*wall_thickness, enclosure_width - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate

vent_center_z = enclosure_height - vent_offset_from_top - vent_slot_height/2
vent_cut = Pos(enclosure_length/2 - wall_thickness/2, 0, vent_center_z) * Box(wall_thickness, vent_slot_width, vent_slot_height)
solid_body = solid_body - vent_cut

hole_positions = [
    (-enclosure_length/2 + mount_hole_offset, -enclosure_width/2 + mount_hole_offset),
    (enclosure_length/2 - mount_hole_offset, -enclosure_width/2 + mount_hole_offset),
    (-enclosure_length/2 + mount_hole_offset, enclosure_width/2 - mount_hole_offset),
    (enclosure_length/2 - mount_hole_offset, enclosure_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, enclosure_height/2) * Cylinder(mount_hole_diameter/2, enclosure_height)

rib1 = Pos(-enclosure_length/2 + wall_thickness + rib_width/2, 0, enclosure_height/2) * Box(rib_width, rib_thickness, rib_height)
rib2 = Pos(enclosure_length/2 - wall_thickness - rib_width/2, 0, enclosure_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "enclosure_with_vents_and_ribs"
export_step(part, "output.step")
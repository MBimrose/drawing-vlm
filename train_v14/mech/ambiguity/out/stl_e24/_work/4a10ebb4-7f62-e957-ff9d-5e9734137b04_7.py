from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
base_thickness = 4.0
vent_slot_width = 30.0
vent_slot_height = 10.0
vent_slot_offset_z = 5.0
mount_hole_diameter = 3.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = 5.0
chamfer_distance = 0.5

base = Pos(0, 0, base_thickness/2) * Box(enclosure_length - 2*wall_thickness, enclosure_width - 2*wall_thickness, base_thickness)

outer_box = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)
bottom_face = outer_box.faces().sort_by(Axis.Z)[0]
shell = offset(outer_box, amount=-wall_thickness, openings=[bottom_face])

result = base + shell

vent_slot = Pos(0, enclosure_width/2 - wall_thickness/2, enclosure_height/2 + vent_slot_offset_z) * Box(vent_slot_width, wall_thickness, vent_slot_height)
result = result - vent_slot

hole_positions = [
    (-enclosure_length/2 + mount_hole_offset, -enclosure_width/2 + mount_hole_offset),
    ( enclosure_length/2 - mount_hole_offset, -enclosure_width/2 + mount_hole_offset),
    (-enclosure_length/2 + mount_hole_offset,  enclosure_width/2 - mount_hole_offset),
    ( enclosure_length/2 - mount_hole_offset,  enclosure_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, enclosure_height/2) * Cylinder(mount_hole_diameter/2, enclosure_height + 10)

rib = Pos(0, 0, -rib_height/2) * Box(enclosure_length - 2*wall_thickness, rib_thickness, rib_height)
result = result + rib

part = result
part.name = "enclosure_with_vents"
export_step(part, "output.step")
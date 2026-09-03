from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 12.0
num_slots = 3
fillet_radius = 1.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0
rib_width = 8.0
rib_height = 2.0
rib_offset = 5.0

solid_body = Box(plate_length, plate_width, plate_thickness)

for i in range(num_slots):
    x = (i - (num_slots - 1) / 2) * (slot_width + slot_spacing)
    solid_body = solid_body - Pos(x, 0, 0) * Box(slot_width, slot_length, plate_thickness)

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

rib1 = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
solid_body = solid_body + rib1 + rib2

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_slots_ribs"
export_step(part, "output.step")
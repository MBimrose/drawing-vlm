from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 8.0
flange_width = 10.0
slot_length = 30.0
slot_width = 6.0
slot_spacing = 15.0
num_slots = 4
mount_hole_dia = 5.0
mount_hole_offset = 10.0
rib_height = 6.0
rib_thickness = 4.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Box(plate_length, rib_thickness, rib_height)
result = base + rib

slot_start_y = -((num_slots - 1) * slot_spacing) / 2.0
for i in range(num_slots):
    y = slot_start_y + i * slot_spacing
    slot = Pos(0, y, 0) * Box(slot_length, slot_width, plate_thickness + 2)
    result = result - slot

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 2)
    result = result - hole

part = result
part.name = "plate_with_rib_slots_and_holes"
export_step(part, "output.step")
from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 8.0
boss_diameter = 20.0
boss_height = 4.0
slot_length = 30.0
slot_width = 6.0
slot_spacing = 15.0
num_slots = 4
mount_hole_dia = 5.0
mount_hole_offset = 10.0
rib_width = 6.0
rib_height = 3.0
rib_spacing = 30.0

result = Box(plate_length, plate_width, plate_thickness)
result = result + Cylinder(boss_diameter/2, boss_height)

for i in range(num_slots):
    y = (i - (num_slots-1)/2) * slot_spacing
    result = result - Pos(0, y, 0) * Box(slot_length, slot_width, plate_thickness + 10)

corner_x = plate_length/2 - mount_hole_offset
corner_y = plate_width/2 - mount_hole_offset
for x, y in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 10)

rib_count = int((plate_width - 2*mount_hole_offset) // rib_spacing)
for i in range(rib_count):
    y = -plate_width/2 + mount_hole_offset + (i + 0.5) * rib_spacing
    result = result + Pos(0, y, -plate_thickness/2 + rib_height/2) * Box(plate_length - 2*mount_hole_offset, rib_width, rib_height)

part = result
part.name = "plate_with_boss_slots_ribs"
export_step(part, "output.step")
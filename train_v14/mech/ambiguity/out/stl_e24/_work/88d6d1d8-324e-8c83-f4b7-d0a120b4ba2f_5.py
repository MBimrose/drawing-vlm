from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 2.0
slot_length = 12.0
slot_width = 3.0
slot_spacing_x = 15.0
slot_spacing_y = 8.0
num_slots_x = 4
num_slots_y = 5
mount_hole_dia = 4.0
mount_hole_offset = 6.0
rib_width = 10.0
rib_height = 1.5
chamfer_size = 0.5

result = Box(plate_width, plate_height, plate_thickness)

for i in range(num_slots_x):
    for j in range(num_slots_y):
        x = (i - (num_slots_x - 1) / 2) * slot_spacing_x
        y = (j - (num_slots_y - 1) / 2) * slot_spacing_y
        result = result - Pos(x, y, plate_thickness / 2) * Box(slot_length, slot_width, plate_thickness)

hole_positions = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_height/2 - mount_hole_offset),
    (plate_width/2 - mount_hole_offset, plate_height/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, plate_thickness)

rib = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width, rib_height)
result = result + rib

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_slots_ribs"
export_step(part, "output.step")
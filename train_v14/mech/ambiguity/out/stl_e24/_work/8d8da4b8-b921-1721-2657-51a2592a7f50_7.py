from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 25.0
slot_width = 6.0
slot_offset_y = 18.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
chamfer_size = 0.5

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

slot1 = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
slot2 = Pos(0, -slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - slot1 - slot2

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

part = result
part.name = "plate_with_pockets_slots_and_holes"
export_step(part, "output.step")
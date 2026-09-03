from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
slot_length = 25.0
slot_width = 6.0
slot_offset_y = 20.0
rib_height = 2.0
rib_width = 10.0
rib_thickness = 4.0
chamfer_size = 0.2

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

result = result - Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - Pos(0, -slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)

rib = Pos(-plate_length/2 + rib_thickness/2, 0, -plate_thickness/2 + rib_height/2) * Box(rib_thickness, rib_width, rib_height)
result = result + rib

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_pocket_holes_slots_rib"
export_step(part, "output.step")
from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 25.0
slot_width = 6.0
slot_offset = 20.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 15.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

slot1 = Pos(0, slot_offset, 0) * Box(slot_length, slot_width, plate_thickness)
slot2 = Pos(0, -slot_offset, 0) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot1 - slot2

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

rib_count = int((plate_length - 2*mount_hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -plate_length/2 + mount_hole_offset + i * rib_spacing
    rib = Pos(x_pos, 0, -plate_thickness/2 + rib_height/2) * Box(rib_thickness, plate_width - 2*mount_hole_offset, rib_height)
    solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_pockets_slots_ribs"
export_step(part, "output.step")
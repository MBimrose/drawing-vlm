from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 8.0
slot_length = 30.0
slot_width = 6.0
slot_spacing = 15.0
num_slots = 4
boss_diameter = 20.0
boss_height = 4.0
chamfer_size = 0.5
mount_hole_dia = 5.0
mount_hole_offset = 10.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body + Cylinder(boss_diameter / 2, boss_height)

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, plate_thickness + boss_height + 10)

slot_start_y = -((num_slots - 1) * slot_spacing) / 2
for i in range(num_slots):
    y = slot_start_y + i * slot_spacing
    solid_body = solid_body - Pos(0, y, 0) * Box(slot_length, slot_width, plate_thickness + boss_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_slots_and_holes"
export_step(part, "output.step")
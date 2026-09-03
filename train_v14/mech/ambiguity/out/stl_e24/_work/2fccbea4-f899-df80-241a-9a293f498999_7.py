from build123d import *

plate_width = 100
plate_height = 80
plate_thickness = 8
slot_length = 30
slot_width = 6
slot_spacing = 15
num_slots = 4
boss_diameter = 20
boss_height = 4
mount_hole_dia = 5
mount_hole_offset = 10
chamfer_dist = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = solid_body + Cylinder(boss_diameter/2, boss_height)

for i in range(num_slots):
    y = -((num_slots-1)/2)*slot_spacing + i*slot_spacing
    solid_body = solid_body - Pos(0, y, 0) * Box(slot_length, slot_width, plate_thickness + 1)

corner_coords = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_height/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_height/2 - mount_hole_offset)
]
for x, y in corner_coords:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 1)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "plate_with_slots_and_boss"
export_step(part, "output.step")
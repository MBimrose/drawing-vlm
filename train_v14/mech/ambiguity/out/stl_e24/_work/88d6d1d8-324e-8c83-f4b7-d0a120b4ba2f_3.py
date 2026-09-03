from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 2.0
rib_width = 10.0
rib_height = 1.5
slot_length = 12.0
slot_width = 3.0
slot_spacing_x = 15.0
slot_spacing_y = 12.0
slot_rows = 3
slot_cols = 4
chamfer_distance = 0.2
mount_hole_diameter = 4.0
mount_hole_offset = 6.0

solid_body = Box(plate_length, plate_width, plate_thickness)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

slot_points = []
start_x = -plate_length/2 + slot_spacing_x
start_y = -plate_width/2 + slot_spacing_y
for i in range(slot_cols):
    for j in range(slot_rows):
        x = start_x + i*slot_spacing_x
        y = start_y + j*slot_spacing_y
        slot_points.append((x, y))

for x, y in slot_points:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness * 2)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_length, rib_height)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_rib_and_slots"
export_step(part, "output.step")
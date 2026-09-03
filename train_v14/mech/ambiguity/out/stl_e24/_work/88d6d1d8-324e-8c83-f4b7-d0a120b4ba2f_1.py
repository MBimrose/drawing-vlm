from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 2.0
rib_width = 10.0
rib_height = 1.5
slot_length = 12.0
slot_width = 3.0
slot_spacing_x = 15.0
slot_spacing_y = 12.0
slot_rows = 4
slot_cols = 5
mount_hole_diameter = 4.0
mount_hole_offset = 6.0
chamfer_size = 0.4

solid_body = Box(plate_width, plate_depth, plate_thickness)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_depth/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_depth/2 - mount_hole_offset)
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

rib = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body + rib

slot_points = []
for row in range(slot_rows):
    y = -plate_depth/2 + slot_spacing_y + row * slot_spacing_y
    x_offset = slot_spacing_x/2 if row % 2 else 0
    for col in range(slot_cols):
        x = -plate_width/2 + slot_spacing_x + col * slot_spacing_x + x_offset
        if abs(x) + slot_length/2 > plate_width/2 - mount_hole_offset:
            continue
        slot_points.append((x, y))

for x, y in slot_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_slots"
export_step(part, "output.step")
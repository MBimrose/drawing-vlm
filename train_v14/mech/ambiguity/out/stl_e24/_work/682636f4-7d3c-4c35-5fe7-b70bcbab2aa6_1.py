from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 3.0
vent_hole_diameter = 3.0
vent_rows = 4
vent_cols = 6
vent_spacing_x = 8.0
vent_spacing_y = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
chamfer_distance = 1.0
slot_width = 2.0
slot_length = 30.0
slot_spacing = 10.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

vent_origin_x = -((vent_cols - 1) * vent_spacing_x) / 2
vent_origin_y = -((vent_rows - 1) * vent_spacing_y) / 2
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_origin_x + i * vent_spacing_x
        y = vent_origin_y + j * vent_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, plate_thickness + 1)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

num_slots = int((pocket_length - slot_spacing) // slot_spacing) + 1
slot_origin_x = -pocket_length/2 + slot_spacing/2
for i in range(num_slots):
    x = slot_origin_x + i * slot_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Box(slot_width, slot_length, plate_thickness + 1)

part = solid_body
part.name = "ventilated_plate"
export_step(part, "output.step")
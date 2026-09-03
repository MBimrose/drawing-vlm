from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 2.0
vent_slot_length = 12.0
vent_slot_width = 3.0
vent_spacing_x = 15.0
vent_spacing_y = 8.0
vent_rows = 3
vent_columns = 4
mount_hole_diameter = 4.0
mount_hole_offset = 6.0
rib_width = 10.0
rib_height = 1.5
chamfer_distance = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

for i in range(vent_columns):
    for j in range(vent_rows):
        x = (i - (vent_columns - 1) / 2) * vent_spacing_x
        y = (j - (vent_rows - 1) / 2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Box(vent_slot_length, vent_slot_width, plate_thickness)

corner_x = plate_length / 2 - mount_hole_offset
corner_y = plate_width / 2 - mount_hole_offset
for cx, cy in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    solid_body = solid_body - Pos(cx, cy, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness)

rib1 = Pos(0, 0, plate_thickness / 2 + rib_height / 2) * Box(rib_width, plate_length, rib_height)
rib2 = Pos(0, 0, plate_thickness / 2 + rib_height / 2) * Box(plate_width, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "ventilated_plate_with_ribs"
export_step(part, "output.step")
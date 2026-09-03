from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
vent_hole_diameter = 4.0
vent_rows = 4
vent_cols = 5
vent_spacing_x = 12.0
vent_spacing_y = 12.0
vent_offset_x = 10.0
vent_offset_y = 10.0

solid = Box(plate_length, plate_width, plate_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)

mount_pts = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in mount_pts:
    solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

vent_pts = []
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_offset_x + i * vent_spacing_x
        y = vent_offset_y + j * vent_spacing_y
        if x <= plate_length/2 - vent_offset_x and y <= plate_width/2 - vent_offset_y:
            vent_pts.append((x, y))

for x, y in vent_pts:
    solid = solid - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, plate_thickness * 2)

part = solid
part.name = "ventilated_plate"
export_step(part, "output.step")
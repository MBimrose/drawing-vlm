from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_width = 20.0
rib_depth = 10.0
rib_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
hole_offset_x = 30.0
hole_offset_y = 20.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

rib = Pos(0, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

hole_points = []
for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = hole_offset_y + (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole_points.append((x, y))
for x, y in hole_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")
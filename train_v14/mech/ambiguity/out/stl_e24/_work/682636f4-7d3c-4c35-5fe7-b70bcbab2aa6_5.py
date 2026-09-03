from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 3.0
hole_diameter = 3.0
hole_spacing_x = 8.0
hole_spacing_y = 8.0
hole_rows = 4
hole_cols = 6
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
chamfer_size = 1.0
rib_width = 2.0
rib_height = 2.0
rib_spacing = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib1 = Pos(-rib_spacing/2, 0, rib_height/2) * Box(rib_width, plate_width - 2*mount_hole_offset, rib_height)
rib2 = Pos(rib_spacing/2, 0, rib_height/2) * Box(rib_width, plate_width - 2*mount_hole_offset, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")
from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
cutout_diameter = 30.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
num_holes_x = 3
num_holes_y = 2
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
rib_thickness = 4.0
rib_height = plate_height * 0.6

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(cutout_diameter/2, plate_thickness + 10)

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x-1)/2) * hole_spacing_x
        z = (j - (num_holes_y-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

mount_points = [(-plate_width/2 + mount_hole_offset, 0), (plate_width/2 - mount_hole_offset, 0)]
for x, z in mount_points:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

rib = Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + Pos(plate_width/2 + rib_thickness/2, -plate_thickness/2 - rib_thickness/2, 0) * rib
solid_body = solid_body + Pos(-plate_width/2 - rib_thickness/2, -plate_thickness/2 - rib_thickness/2, 0) * rib

part = solid_body
part.name = "plate_with_cutouts_and_ribs"
export_step(part, "output.step")
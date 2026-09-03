from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
central_hole_diameter = 30.0
mount_hole_diameter = 6.0
mount_hole_spacing = 60.0
clearance_hole_diameter = 5.0
clearance_rows = 2
clearance_cols = 5
clearance_spacing_x = 12.0
clearance_spacing_y = 12.0
rib_width = 4.0
rib_height = 4.0
rib_length = plate_height - 20.0

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(central_hole_diameter/2, plate_thickness + 2)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 2)

for i in range(clearance_cols):
    for j in range(clearance_rows):
        x = (i - (clearance_cols-1)/2) * clearance_spacing_x
        z = (j - (clearance_rows-1)/2) * clearance_spacing_y
        solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, plate_thickness + 2)

rib = Box(rib_width, rib_height, rib_length)
solid_body = solid_body + Pos(plate_width/2 + rib_width/2, -plate_height/2 + rib_height/2, 0) * rib
solid_body = solid_body + Pos(-plate_width/2 - rib_width/2, -plate_height/2 + rib_height/2, 0) * rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
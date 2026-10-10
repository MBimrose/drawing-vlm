from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
central_hole_diameter = 30.0
clearance_hole_diameter = 5.0
clearance_hole_spacing_x = 20.0
clearance_hole_spacing_y = 12.0
clearance_hole_rows = 2
clearance_hole_cols = 3
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
rib_width = 4.0
rib_height = 30.0
rib_depth = 4.0
chamfer_size = 0.8

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(central_hole_diameter/2, plate_thickness + 1)

for i in range(clearance_hole_cols):
    for j in range(clearance_hole_rows):
        x = (i - (clearance_hole_cols - 1) / 2) * clearance_hole_spacing_x
        z = (j - (clearance_hole_rows - 1) / 2) * clearance_hole_spacing_y
        solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, plate_thickness + 1)

for x in [-plate_width/2 + mount_hole_offset, plate_width/2 - mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Y), chamfer_size)

rib = Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + Pos(plate_width/2 + rib_width/2, -plate_thickness/2 - rib_depth/2, 0) * rib
solid_body = solid_body + Pos(-plate_width/2 - rib_width/2, -plate_thickness/2 - rib_depth/2, 0) * rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
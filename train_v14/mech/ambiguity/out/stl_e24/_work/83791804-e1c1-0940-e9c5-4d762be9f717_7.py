from build123d import *

bracket_width = 80.0
bracket_height = 50.0
bracket_thickness = 6.0
cutout_diameter = 30.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
rib_width = 4.0
rib_height = bracket_height * 0.6
rib_depth = 4.0

solid_body = Box(bracket_width, bracket_thickness, bracket_height)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(cutout_diameter/2, bracket_thickness)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        z = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness)

for x in [-bracket_width/2 + mount_hole_offset, bracket_width/2 - mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness)

solid_body = solid_body + Pos(-bracket_width/2 - rib_depth/2, 0, 0) * Box(rib_depth, rib_width, rib_height)
solid_body = solid_body + Pos(bracket_width/2 + rib_depth/2, 0, 0) * Box(rib_depth, rib_width, rib_height)

part = solid_body
part.name = "bracket_with_ribs"
export_step(part, "output.step")
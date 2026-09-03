from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 8.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 25.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 30.0
mount_hole_diameter = 8.0
mount_hole_spacing = 20.0
mount_hole_offset = 15.0

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(hole_offset - arm_length/2, 0, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(-arm_length/2 + mount_hole_offset, y, 0) * Cylinder(mount_hole_diameter/2, arm_thickness * 2)

solid_body = solid_body - Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

rib_x = -arm_length/2 + rib_offset
solid_body = solid_body + Pos(rib_x, 0, -arm_thickness/2) * Box(rib_width, rib_height, arm_thickness)

part = solid_body
part.name = "arm_with_rib"
export_step(part, "output.step")
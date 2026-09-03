from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 6.0
notch_width = 10.0
notch_depth = 4.0
notch_height = 3.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 4
fillet_radius = 0.5
rib_width = 8.0
rib_height = 2.0
rib_offset = 10.0
pocket_width = 6.0
pocket_depth = 4.0
pocket_offset = 15.0

solid_body = Box(arm_length, arm_width, arm_thickness)

notch = Pos(arm_length/2 - notch_depth/2, 0, 0) * Box(notch_depth, notch_width, arm_thickness)
solid_body = solid_body - notch

rib = Pos(-arm_length/2 + rib_offset, 0, -arm_thickness/2 + rib_height/2) * Box(rib_width, arm_width - 2*rib_offset, rib_height)
solid_body = solid_body + rib

pocket = Pos(-arm_length/2 + pocket_offset, 0, 0) * Box(pocket_width, pocket_depth, arm_thickness)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "arm_with_notch_rib_pocket_holes"
export_step(part, "output.step")
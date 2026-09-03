from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 12.0
groove_width = 12.0
groove_depth = 6.0
fillet_radius = 2.0
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 2
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 5.0

solid = Box(arm_length, arm_width, arm_thickness)
solid = solid - Pos(0, arm_width/2 - groove_depth/2, 0) * Box(groove_width, groove_depth, arm_length)
solid = fillet(solid.edges(), fillet_radius)
solid = solid - Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness)

part = solid
part.name = "arm_with_groove_pocket_holes"
export_step(part, "output.step")
from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 12.0
groove_width = 12.0
groove_depth = 5.0
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 4.0
rib_length = 40.0

base = Box(arm_length, arm_width, arm_thickness)

groove = Pos(0, arm_width/2 - groove_depth/2, arm_thickness/2) * Box(groove_width, groove_depth, arm_thickness)
base = base - groove

base = fillet(base.edges(), fillet_radius)

rib = Pos(0, 0, -arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
base = base + rib

hole_r = hole_diameter / 2
hole_cyl = Cylinder(hole_r, arm_thickness + 10)
for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        base = base - Pos(x, y, arm_thickness/2) * hole_cyl

part = base
part.name = "arm_with_groove_rib_holes"
export_step(part, "output.step")
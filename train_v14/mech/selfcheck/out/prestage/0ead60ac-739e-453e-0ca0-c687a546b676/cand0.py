from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
rib_height = 5.0
rib_width = 6.0
rib_offset = 4.0
pocket_depth = 6.0
pocket_margin = 2.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Box(arm_length, arm_width, arm_thickness)
rib = Pos(0, arm_width/2 - rib_offset, 0) * Box(rib_width, rib_height, arm_thickness)
result = base + rib

pocket_w = arm_width - 2 * pocket_margin
pocket_l = arm_length - 2 * pocket_margin
pocket = Pos(0, 0, arm_thickness - pocket_depth/2) * Box(pocket_w, pocket_l, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

result = chamfer(result.edges().filter_by(Axis.X), chamfer_size)

part = result
part.name = "arm_with_rib_pocket_holes"
export_step(part, "output.step")
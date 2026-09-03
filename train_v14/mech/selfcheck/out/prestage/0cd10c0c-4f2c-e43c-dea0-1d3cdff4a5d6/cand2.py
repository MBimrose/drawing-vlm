from build123d import *

arm_length = 80
arm_width = 20
arm_thickness = 10
tab_length = 30
tab_width = 10
pocket_length = 20
pocket_width = 10
pocket_depth = 4
hole_diameter = 4
hole_spacing = 12
hole_count = 6
hole_offset = 15
chamfer_size = 1

base = Box(arm_length, arm_width, arm_thickness)
tab = Pos(arm_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
result = base + tab

pocket = Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(hole_count):
    x = -arm_length/2 + hole_offset + i * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_tab"
export_step(part, "output.step")
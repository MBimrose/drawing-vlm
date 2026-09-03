from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
tab_length = 30.0
tab_width = 10.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset_from_end = 15.0
chamfer_size = 1.0

base_arm = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
tab = Pos(arm_length + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
result = base_arm + tab

pocket = Pos(arm_length/2, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(6):
    x = hole_offset_from_end + i * hole_spacing
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness)
    result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_tab_pocket_and_holes"
export_step(part, "output.step")
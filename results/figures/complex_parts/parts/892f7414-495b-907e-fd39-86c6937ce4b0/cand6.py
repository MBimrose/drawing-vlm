from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 5.0
rib_count = 4
hole_diameter = 10.0
chamfer_size = 0.5
tab_length = 12.0
tab_width = 6.0
tab_thickness = 4.0

result = Box(arm_length, arm_width, arm_thickness)

for i in range(rib_count):
    y_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(-arm_length/2 + rib_spacing + rib_thickness/2, y_pos, 0) * Box(rib_thickness, rib_height, arm_thickness + rib_height)
    result = result + rib

tab = Pos(-arm_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
result = result + tab

result = result - Cylinder(hole_diameter/2, arm_thickness + 2)

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "arm_with_ribs_and_tab"
export_step(part, "output.step")
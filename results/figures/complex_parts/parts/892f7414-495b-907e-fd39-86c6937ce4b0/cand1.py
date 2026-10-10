from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
hole_diameter = 10.0
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 5.0
rib_count = int((arm_width - rib_spacing) // rib_spacing)
tab_width = 6.0
tab_thickness = 4.0
tab_length = 20.0

result = Box(arm_length, arm_width, arm_thickness)
result = result - Cylinder(hole_diameter/2, arm_thickness)

for i in range(rib_count):
    y_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(-arm_length/2 + rib_spacing + rib_thickness/2, y_pos, 0) * Box(rib_thickness, rib_height, arm_width)
    result = result + rib

tab = Pos(-arm_length/2 + tab_length/2, 0, -arm_thickness/2 - tab_thickness/2) * Box(tab_width, tab_thickness, tab_length)
result = result + tab

part = result
part.name = "arm_with_ribs_and_tab"
export_step(part, "output.step")
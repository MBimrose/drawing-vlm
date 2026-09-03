from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 8.0
tab_length = 20.0
tab_width = 12.0
notch_width = 6.0
notch_depth = 12.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_angle = 82.0
chamfer_size = 0.2

base = Box(arm_length, arm_width, arm_thickness)
tab = Pos(arm_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
result = base + tab

notch = Pos(arm_length/2 + tab_length/2, tab_width/2 - notch_width/2, 0) * Box(notch_depth, notch_width, arm_thickness)
result = result - notch

hole_positions = [(-arm_length/3, -arm_width/4), (arm_length/3, -arm_width/4)]
for x, y in hole_positions:
    result = result - Pos(x, y, arm_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, arm_thickness, countersink_angle)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_tab"
export_step(part, "output.step")
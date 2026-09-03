from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 8.0
tab_length = 20.0
tab_width = 15.0
slot_width = 6.0
slot_depth = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_angle = 82.0
chamfer_distance = 1.0

arm = Box(arm_length, arm_width, arm_thickness)
tab = Pos(arm_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
result = arm + tab

slot_cut = Pos(arm_length/2 + tab_length - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, arm_thickness)
result = result - slot_cut

hole_positions = [(-arm_length/3, -arm_width/4), (arm_length/3, -arm_width/4)]
for x, y in hole_positions:
    hole = Pos(x, y, arm_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, arm_thickness, countersink_angle)
    result = result - hole

part = result
part.name = "arm_with_tab"
export_step(part, "output.step")
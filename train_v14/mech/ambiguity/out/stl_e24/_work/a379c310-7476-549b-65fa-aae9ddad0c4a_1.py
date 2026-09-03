from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 8.0
tab_length = 15.0
tab_width = 12.0
slot_width = 6.0
slot_length = 12.0
slot_offset_from_end = 5.0
hole_diameter = 4.0
countersink_diameter = 6.5
countersink_angle = 82.0
hole_spacing = 50.0
chamfer_distance = 1.0

base = Box(arm_length, arm_width, arm_thickness)
tab = Pos(arm_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
result = base + tab

slot_center_x = arm_length/2 + tab_length - slot_offset_from_end - slot_length/2
slot = Pos(slot_center_x, 0, 0) * Box(slot_width, slot_length, arm_thickness)
result = result - slot

for x, y in [(-hole_spacing/2, -arm_width/4), (hole_spacing/2, -arm_width/4)]:
    csk = Pos(x, y, arm_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, arm_thickness, countersink_angle)
    result = result - csk

x_face = result.faces().sort_by(Axis.X)[-1]
result = chamfer(x_face.edges(), chamfer_distance)

part = result
part.name = "arm_with_tab"
export_step(part, "output.step")
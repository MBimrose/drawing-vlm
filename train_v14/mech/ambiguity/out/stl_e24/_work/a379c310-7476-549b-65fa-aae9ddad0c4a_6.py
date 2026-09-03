from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 8.0
rib_height = 4.0
rib_width = 6.0
rib_offset = 10.0
slot_width = 6.0
slot_length = 30.0
slot_offset = 5.0
hole_diameter = 4.0
csk_diameter = 8.0
csk_angle = 82.0
csk_depth = 2.0

base = Box(arm_length, arm_width, arm_thickness)
rib = Pos(arm_length/2 - rib_offset, 0, 0) * Box(rib_width, rib_height, arm_thickness)
solid_body = base + rib

slot_cut = Pos(arm_length/2 - slot_offset, arm_width/2 - arm_thickness/2, 0) * Box(slot_length, arm_thickness, slot_width)
solid_body = solid_body - slot_cut

for x in [-arm_length/3, arm_length/3]:
    hole = Pos(x, 0, arm_thickness/2) * CounterSinkHole(hole_diameter/2, csk_diameter/2, csk_depth, csk_angle)
    solid_body = solid_body - hole

part = solid_body
part.name = "arm_with_rib_slot_holes"
export_step(part, "output.step")
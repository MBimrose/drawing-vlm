from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
flange_length = 30.0
flange_width = 30.0
flange_thickness = arm_thickness
hole_diameter = 10.0
hole_offset_from_end = 6.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
slot_width = 8.0
slot_depth = 6.0
slot_offset_from_end = 10.0
slot_length = 40.0

arm = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
flange = Pos(-flange_length/2, 0, 0) * Box(flange_length, flange_width, flange_thickness)
result = arm + flange

result = result - Pos(arm_length - hole_offset_from_end, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + 1)

for x in [-flange_length/2 - mount_hole_spacing/2, -flange_length/2 + mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, flange_thickness + 1)

slot_center_x = -flange_length + slot_offset_from_end + slot_length/2
result = result - Pos(slot_center_x, 0, arm_thickness/2 - slot_depth/2) * Box(slot_length, slot_width, slot_depth)

part = result
part.name = "arm_with_flange"
export_step(part, "output.step")
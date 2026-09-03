from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
shoulder_length = 40.0
shoulder_width = 30.0
hole_diameter = 10.0
hole_offset_from_end = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
pocket_length = 30.0
pocket_width = 10.0
pocket_depth = 5.0

shoulder = Pos(shoulder_length/2, 0, arm_thickness/2) * Box(shoulder_length, shoulder_width, arm_thickness)
arm = Pos(shoulder_length + arm_length/2, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
result = shoulder + arm

result = result - Pos(shoulder_length + arm_length - hole_offset_from_end, 0, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)

for x in [shoulder_length/2 - mount_hole_spacing/2, shoulder_length/2 + mount_hole_spacing/2]:
    result = result - Pos(x, 0, arm_thickness/2) * Cylinder(mount_hole_diameter/2, arm_thickness)

pocket_center_x = shoulder_length + arm_length/2 - pocket_length/2
result = result - Pos(pocket_center_x, 0, arm_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

part = result
part.name = "shoulder_arm_with_holes_and_pocket"
export_step(part, "output.step")
from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
shoulder_length = 30.0
shoulder_width = 30.0
pivot_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
fillet_radius = 2.0
pocket_depth = 6.0
pocket_width = 10.0
pocket_length = 40.0

base = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
shoulder = Pos(-shoulder_length/2, 0, 0) * Box(shoulder_length, shoulder_width, arm_thickness)
result = base + shoulder

result = result - Pos(arm_length - pivot_hole_diameter/2, 0, 0) * Cylinder(pivot_hole_diameter/2, arm_thickness * 2)

for x in [-shoulder_length/2 + mount_hole_spacing/2, -shoulder_length/2 - mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, arm_thickness * 2)

result = result - Pos(-shoulder_length/2, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

result = fillet(result.edges().filter_by(Axis.X), fillet_radius)

part = result
part.name = "arm_with_shoulder"
export_step(part, "output.step")
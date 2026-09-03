from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
base_length = 40.0
base_width = 30.0
base_thickness = arm_thickness
pivot_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
rib_width = 8.0
rib_depth = 6.0
rib_length = 50.0
rib_offset = 10.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
arm = Pos(base_length/2 + arm_length/2, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
result = base + arm

pivot_x = base_length/2 + arm_length - arm_thickness/2
result = result - Pos(pivot_x, 0, 0) * Cylinder(pivot_hole_diameter/2, 100)

mount_x1 = -base_length/2 + mount_hole_spacing/2
mount_x2 = base_length/2 - mount_hole_spacing/2
result = result - Pos(mount_x1, 0, 0) * Cylinder(mount_hole_diameter/2, 100)
result = result - Pos(mount_x2, 0, 0) * Cylinder(mount_hole_diameter/2, 100)

rib_x = base_length/2 + rib_offset + rib_length/2
result = result - Pos(rib_x, 0, arm_thickness - rib_depth/2) * Box(rib_length, rib_width, rib_depth)

part = result
part.name = "arm_with_base_and_holes"
export_step(part, "output.step")
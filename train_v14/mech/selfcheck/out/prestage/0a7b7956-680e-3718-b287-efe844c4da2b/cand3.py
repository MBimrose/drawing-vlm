from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
base_length = 40.0
base_width = 30.0
pivot_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
rib_width = 8.0
rib_height = 5.0
rib_length = 60.0
rib_offset = 10.0

base = Box(base_length, base_width, arm_thickness)
arm = Pos(base_length/2 + arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
result = base + arm

result = result - Pos(base_length/2 + arm_length - 6, 0, 0) * Cylinder(pivot_hole_diameter/2, arm_thickness)

for x in [-base_length/2 + mount_hole_spacing/2, base_length/2 - mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, arm_thickness)

rib = Pos(rib_offset, 0, arm_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result - rib

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")
from build123d import *

arm_length = 80.0
arm_width = 20.0
thickness = 12.0
central_hole_dia = 20.0
mount_hole_dia = 6.0
mount_hole_offset = 14.0
fillet_radius = 2.0

base = Box(arm_length, arm_width, thickness) + Box(arm_width, arm_length, thickness)
base = base - Cylinder(central_hole_dia / 2, thickness)

for x, y in [(arm_length/2 - mount_hole_offset, 0), (-(arm_length/2 - mount_hole_offset), 0),
             (0, arm_length/2 - mount_hole_offset), (0, -(arm_length/2 - mount_hole_offset))]:
    base = base - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, thickness)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "cross_arm"
export_step(part, "output.step")
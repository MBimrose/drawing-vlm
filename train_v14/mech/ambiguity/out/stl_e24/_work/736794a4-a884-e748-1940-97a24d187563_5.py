from build123d import *

arm_length = 80.0
arm_width = 20.0
thickness = 12.0
central_hole_dia = 20.0
fillet_radius = 2.0
arm_hole_dia = 6.0
arm_hole_offset = 14.0

vertical = Box(arm_width, arm_length, thickness)
horizontal = Box(arm_length, arm_width, thickness)
base = vertical + horizontal

base = base - Cylinder(central_hole_dia / 2, thickness * 2)

hole_positions = [
    (0, arm_length / 2 - arm_hole_offset),
    (0, -(arm_length / 2 - arm_hole_offset)),
    (arm_length / 2 - arm_hole_offset, 0),
    (-(arm_length / 2 - arm_hole_offset), 0),
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(arm_hole_dia / 2, thickness * 2)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "cross_arm"
export_step(part, "output.step")
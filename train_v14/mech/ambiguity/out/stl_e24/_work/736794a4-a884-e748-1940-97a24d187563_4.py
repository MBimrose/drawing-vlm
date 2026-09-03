from build123d import *

arm_length = 40.0
arm_width = 20.0
thickness = 12.0
central_hole_diameter = 20.0
arm_hole_diameter = 6.0
arm_hole_offset = 14.0
fillet_radius = 2.0

vertical = Box(arm_width, arm_length * 2, thickness)
horizontal = Box(arm_length * 2, arm_width, thickness)
base = vertical + horizontal

base = base - Cylinder(central_hole_diameter / 2, thickness)

for x, y in [(arm_length - arm_hole_offset, 0), (-(arm_length - arm_hole_offset), 0),
             (0, arm_length - arm_hole_offset), (0, -(arm_length - arm_hole_offset))]:
    base = base - Pos(x, y, 0) * Cylinder(arm_hole_diameter / 2, thickness)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "cross_arm"
export_step(part, "output.step")
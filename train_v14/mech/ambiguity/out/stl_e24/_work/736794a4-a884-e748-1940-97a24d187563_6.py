from build123d import *

arm_length = 40.0
arm_width = 20.0
thickness = 12.0
central_hole_dia = 20.0
clearance_hole_dia = 6.0
clearance_offset = arm_length * 0.65
fillet_radius = 2.0

vertical = Box(arm_width, arm_length * 2, thickness)
horizontal = Box(arm_length * 2, arm_width, thickness)
base = vertical + horizontal

base = base - Cylinder(central_hole_dia / 2, thickness)

for x, y in [(clearance_offset, 0), (-clearance_offset, 0), (0, clearance_offset), (0, -clearance_offset)]:
    base = base - Pos(x, y, 0) * Cylinder(clearance_hole_dia / 2, thickness)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "cross_plate"
export_step(part, "output.step")
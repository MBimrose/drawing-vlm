from build123d import *

overall_length = 80
arm_width = 20
thickness = 12
central_hole_diameter = 20
clearance_hole_diameter = 6
clearance_hole_offset = 30
fillet_radius = 2

vertical = Box(arm_width, overall_length, thickness)
horizontal = Box(overall_length, arm_width, thickness)
base = vertical + horizontal

base = base - Cylinder(central_hole_diameter / 2, thickness)

for x, y in [(clearance_hole_offset, 0), (-clearance_hole_offset, 0), (0, clearance_hole_offset), (0, -clearance_hole_offset)]:
    base = base - Pos(x, y, 0) * Cylinder(clearance_hole_diameter / 2, thickness)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "cross_plate"
export_step(part, "output.step")
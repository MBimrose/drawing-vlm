from build123d import *

arm_length = 80.0
arm_width = 20.0
thickness = 12.0
hub_diameter = 40.0
central_hole_diameter = 20.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_offset = 14.0

vertical = Box(arm_width, arm_length, thickness)
horizontal = Box(arm_length, arm_width, thickness)
base = vertical + horizontal

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

base = base - Cylinder(central_hole_diameter / 2, thickness * 2)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    base = base - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, thickness * 2)

part = base
part.name = "cross_plate"
export_step(part, "output.step")
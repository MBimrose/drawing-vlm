from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
keyway_width = 5.0
keyway_length = 70.0
relief_width = 12.0
relief_depth = 5.0
relief_offset = 15.0
mount_hole_dia = 4.0
mount_hole_count = 3
mount_hole_radius = (outer_diameter / 2) - 10.0
chamfer_size = 1.0

result = Cylinder(outer_diameter / 2, thickness)
result = result - Cylinder(inner_diameter / 2, thickness)
result = result - Box(keyway_length, keyway_width, thickness)
result = result - Pos(0, relief_offset, 0) * Box(relief_width, relief_depth, thickness)
result = result - Pos(0, -relief_offset, 0) * Box(relief_width, relief_depth, thickness)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(mount_hole_dia / 2, thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "flanged_disc_with_keyway"
export_step(part, "output.step")
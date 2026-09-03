from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
length = 40.0
relief_groove_diameter = 40.0
relief_groove_depth = 5.0
relief_groove_position = 15.0
mount_hole_diameter = 5.0
mount_hole_radius = 35.0
chamfer_size = 1.0
rib_width = 5.0
rib_height = 3.0
rib_count = 3

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
relief_groove_radius = relief_groove_diameter / 2.0

result = Pos(0, 0, length / 2) * Cylinder(outer_radius, length)
result = result - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)
result = result - Pos(0, 0, relief_groove_position + relief_groove_depth / 2) * Cylinder(relief_groove_radius, relief_groove_depth)

for i in range(3):
    angle = math.radians(i * 120.0)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    result = result - Pos(px, py, length / 2) * Cylinder(mount_hole_diameter / 2, length)

result = chamfer(result.edges(), chamfer_size)

rib = Pos(outer_radius - rib_width / 2, 0, length / 2) * Box(rib_width, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    ribs = ribs + Rot(0, 0, i * 360.0 / rib_count) * rib

result = result + ribs

part = result
part.name = "hollow_cylinder_with_groove_and_ribs"
export_step(part, "output.step")
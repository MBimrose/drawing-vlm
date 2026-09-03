from build123d import *
import math

outer_radius = 30.0
inner_radius = 22.0
height = 30.0
wall_thickness = outer_radius - inner_radius
rib_thickness = 2.0
rib_width = 5.0
rib_count = 4
keyway_width = 8.0
keyway_depth = 6.0
mount_hole_dia = 4.0
mount_hole_spacing = 20.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = 5.0

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

rib_center_x = inner_radius + rib_thickness / 2
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_center_x, 0, 0) * Box(rib_thickness, rib_width, height)
    result = result + rib

keyway = Pos(inner_radius - keyway_depth / 2, 0, 0) * Box(keyway_width, height, keyway_depth)
result = result - keyway

pocket = Pos(0, outer_radius - pocket_depth / 2, 0) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

hole_radius = mount_hole_dia / 2
hole_depth = wall_thickness + 0.5
for x, y in [(-mount_hole_spacing / 2, 0), (mount_hole_spacing / 2, 0)]:
    hole = Pos(x, y, height / 2 - hole_depth / 2) * Cylinder(hole_radius, hole_depth)
    result = result - hole

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
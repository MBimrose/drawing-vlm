from build123d import *
import math

outer_radius = 30.0
inner_radius = 22.0
length = 30.0
wall_thickness = outer_radius - inner_radius
rib_thickness = 2.0
rib_width = 5.0
rib_count = 4
relief_groove_radius = 2.0
relief_groove_depth = 4.0
relief_groove_position = 20.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = wall_thickness - 1.0
pocket_position = 15.0
chamfer_size = 0.5

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius + rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_width, length)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib
result = result + ribs

groove = Pos(inner_radius - relief_groove_depth / 2, 0, relief_groove_position - length / 2) * Cylinder(relief_groove_radius, length)
result = result - groove

pocket = Pos(0, inner_radius - pocket_depth / 2, pocket_position - length / 2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
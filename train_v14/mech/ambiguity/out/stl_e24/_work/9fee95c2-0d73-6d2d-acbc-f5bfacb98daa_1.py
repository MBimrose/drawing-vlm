from build123d import *

outer_diameter = 60
inner_diameter = 40
length = 50
wall_thickness = (outer_diameter - inner_diameter) / 2
groove_width = 4
groove_depth = 3
rib_count = 6
rib_width = 10
rib_thickness = 4
rib_length = length * 0.6
outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

import math

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove_radius = outer_radius - groove_width
groove = Pos(0, 0, length - groove_depth / 2) * Cylinder(groove_radius, groove_depth)
solid_body = solid_body - groove

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_width / 2.0, 0, rib_length / 2.0) * Box(rib_width, rib_thickness, rib_length)
    solid_body = solid_body + rib

part = solid_body
part.name = "ribbed_cylinder_with_groove"
export_step(part, "output.step")
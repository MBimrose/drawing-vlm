from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 10.0
length = 30.0
knurl_height = 4.0
knurl_width = 2.0
knurl_count = 12
groove_width = 4.0
groove_depth = 2.0
set_screw_diameter = 2.0
set_screw_head_diameter = 4.0
set_screw_head_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - knurl_height / 2.0, 0, length / 2.0) * Box(knurl_width, knurl_height, length)
    result = result + rib

groove = Pos(0, 0, length - groove_width / 2.0) * Cylinder(outer_radius - groove_depth, groove_width)
result = result - groove

set_screw_hole = Pos(outer_radius - wall_thickness / 2.0, 0, length / 2.0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness)
result = result - set_screw_hole

counterbore = Pos(outer_radius - set_screw_head_depth / 2.0, 0, length / 2.0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter / 2.0, set_screw_head_depth)
result = result - counterbore

part = result
part.name = "knurled_bushing"
export_step(part, "output.step")
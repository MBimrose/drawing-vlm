from build123d import *

knob_outer_radius = 30.0
knob_height = 15.0
rib_height = 2.0
rib_width = 4.0
rib_count = 12
central_hole_radius = 5.0
central_hole_depth = 8.0

import math

result = Cylinder(knob_outer_radius, knob_height)

rib_radius = knob_outer_radius - rib_height / 2
for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    rib = Pos(px, py, knob_height / 2) * Rot(0, 0, math.degrees(angle)) * Box(rib_height, rib_width, rib_height)
    result = result + rib

hole = Pos(0, 0, knob_height / 2 - central_hole_depth / 2) * Cylinder(central_hole_radius, central_hole_depth)
result = result - hole

part = result
part.name = "knob_with_ribs"
export_step(part, "output.step")
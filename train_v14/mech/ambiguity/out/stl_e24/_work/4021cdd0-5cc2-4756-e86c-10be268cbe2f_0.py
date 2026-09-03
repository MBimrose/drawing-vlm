from build123d import *

knob_outer_radius = 30.0
knob_height = 16.0
central_hole_radius = 5.0
knurl_rib_width = 2.0
knurl_rib_height = 4.0
knurl_rib_depth = 1.5
knurl_count = 12
top_pocket_width = 12.0
top_pocket_length = 20.0
top_pocket_depth = 4.0
chamfer_distance = 0.8
slot_width = 4.0
slot_height = 6.0
slot_depth = 2.0

import math

result = Cylinder(knob_outer_radius, knob_height)
result = result - Pos(0, 0, knob_height/2) * Cylinder(central_hole_radius, knob_height)

rib_radius = knob_outer_radius - knurl_rib_depth/2
for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    rib = Pos(px, py, knob_height/2) * Rot(0, 0, math.degrees(angle)) * Box(knurl_rib_width, knurl_rib_height, knurl_rib_depth)
    result = result + rib

result = result - Pos(0, 0, knob_height - top_pocket_depth/2) * Box(top_pocket_width, top_pocket_length, top_pocket_depth)
result = result - Pos(knob_outer_radius - slot_depth/2, 0, knob_height/2) * Box(slot_depth, slot_width, slot_height)

part = result
part.name = "knob"
export_step(part, "output.step")
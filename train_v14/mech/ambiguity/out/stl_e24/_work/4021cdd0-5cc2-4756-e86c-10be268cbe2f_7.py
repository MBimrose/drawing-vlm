from build123d import *

knob_outer_radius = 30.0
knob_height = 15.0
rib_width = 2.0
rib_height = 4.0
rib_depth = 1.5
rib_count = 12
rib_offset = 0.5
shaft_radius = 5.0
shaft_depth = 10.0
chamfer_size = 0.5

import math

base = Cylinder(knob_outer_radius, knob_height)

rib_r = knob_outer_radius - rib_offset
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    angle_rad = math.radians(angle_deg)
    px = rib_r * math.cos(angle_rad)
    py = rib_r * math.sin(angle_rad)
    rib = Pos(px, py, knob_height/2 + rib_depth/2) * Rot(0, 0, angle_deg) * Box(rib_width, rib_height, rib_depth)
    base = base + rib

hole = Pos(0, 0, knob_height/2 - shaft_depth/2) * Cylinder(shaft_radius, shaft_depth)
base = base - hole

part = base
part.name = "knob_with_ribs"
export_step(part, "output.step")
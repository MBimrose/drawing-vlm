from build123d import *

knob_outer_radius = 30.0
knob_height = 16.0
rib_width = 2.0
rib_height = 4.0
rib_thickness = 1.5
rib_count = 12
central_hole_radius = 5.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 2.0
set_screw_radius = 2.0
set_screw_depth = 3.0
chamfer_size = 0.5

import math

result = Cylinder(knob_outer_radius, knob_height)
result = result - Pos(0, 0, knob_height/2) * Cylinder(central_hole_radius, knob_height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(knob_outer_radius - rib_width/2, 0, knob_height/2 - rib_height/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

result = result - Pos(0, 0, knob_height - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - Pos(0, 0, knob_height - set_screw_depth/2) * Cylinder(set_screw_radius, set_screw_depth)

part = result
part.name = "knob_with_ribs"
export_step(part, "output.step")
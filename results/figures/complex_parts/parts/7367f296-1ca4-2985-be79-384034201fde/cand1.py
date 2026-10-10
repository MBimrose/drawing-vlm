from build123d import *

knob_outer_radius = 30.0
knob_height = 10.0
boss_radius = 8.0
boss_height = 5.0
central_hole_radius = 5.0
chamfer_distance = 0.5
knurl_count = 12
knurl_width = 2.0
knurl_depth = 1.0

import math

result = Pos(0, 0, knob_height / 2) * Cylinder(knob_outer_radius, knob_height)
result = result + Pos(0, 0, knob_height + boss_height / 2) * Cylinder(boss_radius, boss_height)
result = result - Pos(0, 0, knob_height + boss_height / 2) * Cylinder(central_hole_radius, boss_height)
result = result - Pos(0, 0, (knob_height + boss_height) / 2) * Cylinder(central_hole_radius, knob_height + boss_height)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_distance)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    knurl_cut = Rot(0, 0, angle) * Pos(knob_outer_radius - knurl_depth / 2, 0, knob_height / 2) * Box(knurl_depth, knurl_width, knob_height)
    result = result - knurl_cut

part = result
part.name = "knob"
export_step(part, "output.step")
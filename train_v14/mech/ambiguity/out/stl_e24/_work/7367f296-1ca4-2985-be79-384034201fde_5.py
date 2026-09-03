from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 15.0
knurl_ring_radius = 8.0
knurl_tooth_width = 2.0
knurl_tooth_height = 4.0
knurl_tooth_count = 12
central_hole_radius = 5.0
chamfer_distance = 0.5

result = Cylinder(knob_outer_radius, knob_height)

for i in range(knurl_tooth_count):
    angle = i * 360.0 / knurl_tooth_count
    tooth = Rot(0, 0, angle) * Pos(knurl_ring_radius, 0, knob_height/2 - knurl_tooth_height/2) * Box(knurl_tooth_width, knurl_tooth_height, knurl_tooth_height)
    result = result + tooth

result = result - Cylinder(central_hole_radius, knob_height)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "knob"
export_step(part, "output.step")
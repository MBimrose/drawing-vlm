from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 10.0
hub_radius = 8.0
hub_height = 5.0
slot_width = 2.0
slot_length = 15.0
slot_depth = 4.0
slot_count = 12
central_bore_radius = 5.0
chamfer_distance = 0.5

result = Pos(0, 0, knob_height/2) * Cylinder(knob_outer_radius, knob_height)
result = result + Pos(0, 0, knob_height + hub_height/2) * Cylinder(hub_radius, hub_height)
result = result - Pos(0, 0, (knob_height + hub_height)/2) * Cylinder(central_bore_radius, knob_height + hub_height)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(hub_radius - slot_depth/2, 0, knob_height + hub_height/2) * Box(slot_depth, slot_width, hub_height)
    result = result - slot

z_edges = result.edges().filter_by(Axis.Z)
result = chamfer(z_edges, chamfer_distance)

part = result
part.name = "knob"
export_step(part, "output.step")
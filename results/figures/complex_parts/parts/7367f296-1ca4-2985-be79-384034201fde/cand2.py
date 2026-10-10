from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 10.0
hub_radius = 7.5
hub_height = 5.0
shaft_hole_radius = 5.0
slot_width = 2.0
slot_depth = 4.0
slot_count = 12
chamfer_size = 0.5

result = Pos(0, 0, knob_height / 2) * Cylinder(knob_outer_radius, knob_height)
result = result + Pos(0, 0, knob_height + hub_height / 2) * Cylinder(hub_radius, hub_height)
result = result - Pos(0, 0, (knob_height + hub_height) / 2) * Cylinder(shaft_hole_radius, knob_height + hub_height)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(hub_radius - slot_depth / 2, 0, knob_height + hub_height / 2) * Box(slot_depth, slot_width, hub_height)
    result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "knob"
export_step(part, "output.step")
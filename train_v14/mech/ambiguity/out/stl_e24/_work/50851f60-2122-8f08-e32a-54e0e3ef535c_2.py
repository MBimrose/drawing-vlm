from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
collar_length = 20.0
key_width = 6.0
key_depth = 4.0
slot_width = 4.0
slot_depth = 12.0
slot_count = 4
chamfer_size = 1.0
relief_groove_depth = 2.0
relief_groove_width = 5.0
hole_diameter = 5.0
hole_spacing = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, collar_length)
result = result - Cylinder(inner_radius, collar_length)

keyway = Pos(0, 0, collar_length/2 - key_depth/2) * Box(key_width, collar_length, key_depth)
result = result - keyway

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_width/2, 0, 0) * Box(slot_width, slot_width, slot_depth)
    result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

groove = Pos(0, 0, collar_length/2 - relief_groove_depth/2) * Box(inner_diameter - 2*relief_groove_depth, relief_groove_width, relief_groove_depth)
result = result - groove

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, collar_length)

part = result
part.name = "collar_with_keyway_and_slots"
export_step(part, "output.step")
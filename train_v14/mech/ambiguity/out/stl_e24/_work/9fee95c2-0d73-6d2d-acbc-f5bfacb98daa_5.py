from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
length = 50.0
groove_depth = 3.0
groove_width = 8.0
groove_position = 20.0
slot_width = 4.0
slot_length = 30.0
slot_count = 6
slot_angle_offset = 0.0

result = Cylinder(outer_radius, length)
result = result - Cylinder(inner_radius, length)

groove_cyl = Pos(0, 0, groove_position) * Cylinder(inner_radius - groove_depth, groove_width)
result = result - groove_cyl

for i in range(slot_count):
    angle = i * 360.0 / slot_count + slot_angle_offset
    slot = Rot(0, 0, angle) * Pos(inner_radius + (outer_radius - inner_radius) / 2, 0, length / 2) * Box(outer_radius - inner_radius, slot_width, slot_length)
    result = result - slot

part = result
part.name = "hollow_cylinder_with_groove_and_slots"
export_step(part, "output.step")
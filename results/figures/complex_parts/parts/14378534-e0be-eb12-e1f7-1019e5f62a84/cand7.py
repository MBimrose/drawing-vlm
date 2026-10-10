from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 10.0
length = 30.0
rib_width = 2.0
rib_height = 4.0
rib_count = 12
slot_width = 2.0
slot_depth = 4.0
slot_count = 6
slot_spacing = length / (slot_count + 1)

solid_body = Cylinder(outer_diameter / 2, length)
solid_body = solid_body - Cylinder(inner_diameter / 2, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter / 2 - rib_width / 2, 0, length / 2) * Box(rib_width, rib_height, length)
    solid_body = solid_body + rib

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_diameter / 2 - slot_width / 2, 0, length / 2) * Box(slot_width, slot_depth, length)
    solid_body = solid_body - slot

part = solid_body
part.name = "ribbed_cylinder_with_slots"
export_step(part, "output.step")
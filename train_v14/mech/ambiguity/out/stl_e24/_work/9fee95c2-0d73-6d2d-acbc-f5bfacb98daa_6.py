from build123d import *

outer_radius = 30
inner_radius = 20
length = 50
rib_width = 10
rib_height = 4
rib_count = 4
slot_width = 6
slot_depth = 8
slot_count = 6
groove_width = 4
groove_depth = 2
groove_position = length / 2

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius + rib_height / 2, 0, length / 2) * Box(rib_width, rib_height, length)
for i in range(rib_count):
    angle = i * 360 / rib_count
    result = result + Rot(0, 0, angle) * rib

slot = Pos(outer_radius - slot_depth / 2, 0, length / 2) * Box(slot_width, slot_depth, length)
for i in range(slot_count):
    angle = i * 360 / slot_count
    result = result - Rot(0, 0, angle) * slot

groove = Pos(0, 0, groove_position - groove_width / 2) * Cylinder(outer_radius - groove_depth, groove_width)
result = result - groove

part = result
part.name = "ribbed_cylinder_with_slots_and_groove"
export_step(part, "output.step")
from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
length = 50.0
wall_thickness = outer_radius - inner_radius
groove_depth = 3.0
groove_width = 4.0
groove_position = 0.0
rib_count = 6
rib_thickness = 2.0
rib_height = wall_thickness - 2.0
rib_length = length - 20.0
slot_width = 6.0
slot_length = 30.0
slot_depth = wall_thickness - 1.0

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove = Pos(0, 0, groove_position) * Cylinder(inner_radius - groove_depth, groove_width)
result = result - groove

rib = Pos(inner_radius - rib_height/2, 0, length/2) * Box(rib_height, rib_thickness, rib_length)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

slot = Pos(outer_radius - slot_depth/2, 0, length/2) * Box(slot_depth, slot_width, slot_length)
result = result - slot

part = result
part.name = "hollow_cylinder_with_groove_ribs_slots"
export_step(part, "output.step")
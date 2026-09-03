from build123d import *
import math

outer_radius = 30.0
inner_radius = 22.0
length = 30.0
wall_thickness = outer_radius - inner_radius
slot_width = 6.0
slot_depth = wall_thickness * 0.8
slot_length = length * 0.5
rib_height = 5.0
rib_thickness = 2.0
rib_count = 4
chamfer_size = 0.5

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(inner_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_length, slot_width)
result = result - slot_box

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, length)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_slot_and_ribs"
export_step(part, "output.step")
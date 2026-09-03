from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_width = 4.0
rib_height = 12.0
rib_count = 6
slot_width = 4.0
slot_length = 60.0
slot_depth = wall_thickness - 1.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib_center_x = inner_radius + rib_width / 2.0
rib = Pos(rib_center_x, 0, 0) * Box(rib_width, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

result = result + ribs

slot_center_x = outer_radius - slot_depth / 2.0
slot = Pos(slot_center_x, 0, 0) * Box(slot_depth, slot_length, slot_width)
slots = slot
for i in range(1, 4):
    angle = i * 360.0 / 4
    slots = slots + Rot(0, 0, angle) * slot

result = result - slots

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "ribbed_cylinder_with_slots"
export_step(part, "output.step")
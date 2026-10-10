from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
slot_width = 4.0
slot_length = 12.0
slot_depth = wall_thickness * 0.6
num_slots = 4
chamfer_size = 2.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 3.0
hole_diameter = 6.0
hole_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for i in range(num_slots):
    angle = i * 360.0 / num_slots
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_length, slot_width)
    result = result - slot

for i in range(4):
    angle = i * 360.0 / 4
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
    result = result + rib

for i in range(hole_count):
    angle = i * 360.0 / hole_count
    hole = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Cylinder(hole_diameter / 2.0, wall_thickness * 2.0)
    result = result - hole

part = result
part.name = "hollow_cylinder_with_slots_ribs_holes"
export_step(part, "output.step")
from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_width = 6.0
rib_height = 12.0
rib_count = 6
slot_width = 4.0
slot_length = 30.0
slot_depth = wall_thickness + 0.5
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_width / 2.0, 0, 0) * Box(rib_width, rib_height, length)
    result = result + rib

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
    result = result - slot

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "ribbed_cylinder_with_slots"
export_step(part, "output.step")
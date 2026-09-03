from build123d import *

outer_radius = 35.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 80.0
rib_count = 6
rib_width = 12.0
rib_height = 8.0
rib_thickness = 3.0
slot_count = 6
slot_width = 4.0
slot_length = height * 0.7
slot_depth = wall_thickness * 0.8
chamfer_size = 2.0

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

rib = Pos(inner_radius + rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

slot = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_length)
for i in range(slot_count):
    angle = i * 360.0 / slot_count
    result = result - Rot(0, 0, angle) * slot

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "ribbed_cylinder_with_slots"
export_step(part, "output.step")
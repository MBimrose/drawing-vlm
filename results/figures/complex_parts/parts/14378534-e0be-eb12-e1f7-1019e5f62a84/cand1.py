from build123d import *

outer_diameter = 30.0
inner_diameter = 10.0
length = 30.0
rib_height = 4.0
rib_width = 2.0
rib_count = 12
slot_width = 2.0
slot_depth = 4.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, length)
result = result - Cylinder(inner_radius, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_width / 2.0, 0, length / 2.0) * Box(rib_width, rib_height, length)
    result = result + rib

slot = Pos(outer_radius - slot_depth / 2.0, 0, length / 2.0) * Box(slot_width, slot_depth, length)
result = result - slot

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "ribbed_cylinder_with_slot"
export_step(part, "output.step")
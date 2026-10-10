from build123d import *

outer_diameter = 74.2
inner_diameter = 8.0
thickness = 10.0
counterbore_diameter = 9.0
counterbore_depth = 4.0
chamfer_size = 0.5
rib_width = 4.0
rib_height = 2.0
rib_offset = 5.0
slot_width = 3.0
slot_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, thickness)
result = result - Cylinder(inner_radius, thickness)
result = result - Pos(0, 0, thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

rib = Pos(outer_radius - rib_offset, 0, rib_height/2) * Box(rib_width, rib_height, rib_height)
result = result + rib

slot = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, thickness)
result = result - slot

part = result
part.name = "washer_with_rib_and_slot"
export_step(part, "output.step")
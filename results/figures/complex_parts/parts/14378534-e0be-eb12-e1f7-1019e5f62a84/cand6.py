from build123d import *

outer_diameter = 30.0
inner_diameter = 10.0
length = 42.0
slot_width = 4.0
slot_depth = 2.0
slot_count = 12
chamfer_size = 1.0

solid_body = Cylinder(outer_diameter / 2, length)
solid_body = solid_body - Cylinder(inner_diameter / 2, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_diameter / 2 - slot_depth / 2, 0, length / 2) * Box(slot_depth, slot_width, length)
    solid_body = solid_body - slot

part = solid_body
part.name = "slotted_cylinder"
export_step(part, "output.step")
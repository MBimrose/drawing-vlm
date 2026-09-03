from build123d import *

outer_radius = 30.0
inner_radius = 8.0
length = 80.0
slot_width = 6.0
slot_depth = 12.0
slot_length = 20.0
num_slots = 6
chamfer_size = 2.0

solid_body = Cylinder(outer_radius, length)
solid_body = solid_body - Cylinder(inner_radius, length)

slot_box = Box(slot_depth, slot_width, slot_length)
slot_pos = Pos(outer_radius - slot_depth/2, 0, 0)

for i in range(num_slots):
    angle = i * 360.0 / num_slots
    rotated_slot = Rot(0, 0, angle) * slot_pos * slot_box
    solid_body = solid_body - rotated_slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "cylinder_with_slots"
export_step(part, "output.step")
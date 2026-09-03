from build123d import *
import math

body_radius = 30.0
body_length = 80.0
bore_radius = 8.0
slot_width = 6.0
slot_length = 20.0
slot_depth = 12.0
num_slots = 6
chamfer_size = 2.0

solid_body = Cylinder(body_radius, body_length)
solid_body = solid_body - Cylinder(bore_radius, body_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(num_slots):
    angle = i * 360.0 / num_slots
    slot = Rot(0, 0, angle) * Pos(body_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_length)
    solid_body = solid_body - slot

part = solid_body
part.name = "cylinder_with_slots"
export_step(part, "output.step")
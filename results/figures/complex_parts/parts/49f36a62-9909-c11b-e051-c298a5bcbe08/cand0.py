from build123d import *
import math

inner_diameter = 19.6
outer_diameter = 38.0
height = 15.0
groove_width = 4.0
groove_depth = 2.0
slot_width = 1.0
slot_depth = 2.0
slot_count = 4
chamfer_size = 0.4

inner_radius = inner_diameter / 2.0
outer_radius = outer_diameter / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

groove = Pos(0, 0, height - groove_depth / 2) * Cylinder(inner_radius - groove_width / 2.0, groove_depth)
solid_body = solid_body - groove

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(0, 0, height / 2) * Box(slot_width, outer_diameter, slot_depth)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "grooved_ring_with_slots"
export_step(part, "output.step")
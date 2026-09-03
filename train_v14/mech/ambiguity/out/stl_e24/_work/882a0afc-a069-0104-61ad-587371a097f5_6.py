from build123d import *

outer_radius = 30
wall_thickness = 5
height = 30
slot_width = 4
slot_height = 10
slot_depth = wall_thickness + 1
num_slots = 12
chamfer_size = 2

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

for i in range(num_slots):
    angle = i * 360 / num_slots
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "shelled_cylinder_with_slots"
export_step(part, "output.step")
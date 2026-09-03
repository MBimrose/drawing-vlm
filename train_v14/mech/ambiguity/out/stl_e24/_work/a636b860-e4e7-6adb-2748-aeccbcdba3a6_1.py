from build123d import *

outer_radius = 30.0
inner_radius = 8.0
body_length = 80.0
slot_width = 6.0
slot_length = 20.0
slot_depth = 12.0
slot_count = 6
slot_angle = 360.0 / slot_count
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_radius, -body_length/2), (inner_radius, body_length/2))
            Line((inner_radius, body_length/2), (outer_radius, body_length/2))
            Line((outer_radius, body_length/2), (outer_radius, -body_length/2))
            Line((outer_radius, -body_length/2), (inner_radius, -body_length/2))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

slot_box = Box(slot_depth, slot_width, slot_length)
slot_pos = Pos(outer_radius - slot_depth/2, 0, 0)

for i in range(slot_count):
    angle = i * slot_angle
    rotated_slot = Rot(0, 0, angle) * slot_pos * slot_box
    solid_body = solid_body - rotated_slot

part = solid_body
part.name = "revolved_cylinder_with_slots"
export_step(part, "output.step")
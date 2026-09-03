from build123d import *

outer_radius = 30.0
inner_radius = 8.0
length = 80.0
slot_width = 6.0
slot_depth = 12.0
slot_length = 20.0
slot_spacing_angle = 60.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (inner_radius, length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

num_slots = int(360 / slot_spacing_angle)
for i in range(num_slots):
    angle = i * slot_spacing_angle
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2, 0, length / 2) * Box(slot_depth, slot_width, slot_length)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_cylinder_with_slots"
export_step(part, "output.step")
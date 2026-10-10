from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 40.0
shoulder_length = 10.0
shoulder_diameter = 45.0
slot_width = 5.0
slot_depth = 8.0
slot_count = 4
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, shoulder_length))
            l3 = Line(l2 @ 1, (shoulder_radius, shoulder_length))
            l4 = Line(l3 @ 1, (shoulder_radius, collar_length))
            l5 = Line(l4 @ 1, (inner_radius, collar_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, angle, 0) * Pos(outer_radius - slot_depth / 2.0, collar_length / 2.0, 0) * Box(slot_depth, collar_length, slot_width)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "collar_with_slots"
export_step(part, "output.step")
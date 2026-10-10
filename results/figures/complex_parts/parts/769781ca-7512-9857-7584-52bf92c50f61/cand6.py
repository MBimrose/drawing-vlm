from build123d import *

knob_outer_radius = 28.0
knob_total_height = 45.0
shoulder_height = 10.0
shoulder_radius = 22.0
central_hole_radius = 5.0
central_hole_depth = 30.0
slot_width = 6.0
slot_length = 30.0
chamfer_distance = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (knob_outer_radius, 0))
            l2 = Line(l1 @ 1, (knob_outer_radius, knob_total_height - shoulder_height))
            l3 = Line(l2 @ 1, (shoulder_radius, knob_total_height - shoulder_height))
            l4 = Line(l3 @ 1, (shoulder_radius, knob_total_height))
            l5 = Line(l4 @ 1, (0, knob_total_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

hole = Pos(0, 0, central_hole_depth / 2) * Cylinder(central_hole_radius, central_hole_depth)
solid_body = solid_body - hole

slot = Pos(knob_outer_radius - slot_width / 2, 0, knob_total_height / 2) * Box(slot_width, slot_length, knob_total_height)
solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
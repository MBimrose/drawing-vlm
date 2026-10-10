from build123d import *

knob_outer_radius = 28.0
knob_total_height = 45.0
shoulder_height = 10.0
shoulder_radius = 22.0
central_hole_radius = 5.0
slot_width = 12.0
slot_depth = 8.0
chamfer_distance = 2.0
fillet_radius = 0.5

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
solid_body = solid_body - Cylinder(central_hole_radius, knob_total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

slot_box = Pos(knob_outer_radius - slot_depth / 2, 0, knob_total_height / 2) * Box(slot_depth, knob_total_height * 2, knob_total_height)
solid_body = solid_body - slot_box

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
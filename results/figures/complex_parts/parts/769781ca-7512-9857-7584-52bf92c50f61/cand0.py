from build123d import *

outer_radius = 30.0
wall_thickness = 2.0
knob_height = 45.0
shoulder_height = 10.0
shoulder_radius = 22.0
central_hole_radius = 5.0
slot_width = 6.0
slot_length = 30.0
chamfer_size = 2.0
edge_chamfer = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, knob_height - shoulder_height))
            l3 = Line(l2 @ 1, (shoulder_radius, knob_height - shoulder_height))
            l4 = Line(l3 @ 1, (shoulder_radius, knob_height))
            l5 = Line(l4 @ 1, (0, knob_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_radius, knob_height)

slot_box = Pos(outer_radius - wall_thickness / 2, 0, knob_height / 2) * Box(slot_width, slot_length, knob_height)
solid_body = solid_body - slot_box

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, edge_chamfer)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
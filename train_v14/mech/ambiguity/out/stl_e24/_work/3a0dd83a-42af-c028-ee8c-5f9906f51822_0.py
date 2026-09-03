from build123d import *

knob_total_height = 40.0
knob_base_radius = 12.0
knob_top_radius = 20.0
knob_flare_height = 10.0
shaft_hole_radius = 4.0
counterbore_radius = 6.0
counterbore_depth = 3.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((knob_base_radius, 0), (knob_base_radius, knob_total_height - knob_flare_height))
            l2 = ThreePointArc(l1 @ 1, (knob_base_radius + 2, knob_total_height - knob_flare_height + 2), (knob_top_radius, knob_total_height))
            l3 = Line(l2 @ 1, (0, knob_total_height))
            l4 = Line(l3 @ 1, (knob_base_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, knob_total_height / 2) * Cylinder(shaft_hole_radius, knob_total_height + 10)
solid_body = solid_body - Pos(0, 0, knob_total_height - counterbore_depth / 2) * Cylinder(counterbore_radius, counterbore_depth)
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
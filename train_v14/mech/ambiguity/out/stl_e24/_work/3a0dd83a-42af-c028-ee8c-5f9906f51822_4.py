from build123d import *

knob_base_radius = 12.0
knob_body_height = 30.0
shoulder_radius = 6.0
flange_radius = 20.0
flange_thickness = 4.0
total_height = knob_body_height + shoulder_radius + flange_thickness
shaft_hole_radius = 4.0
counterbore_radius = 6.0
counterbore_depth = 3.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((knob_base_radius, 0), (knob_base_radius, knob_body_height))
            l2 = ThreePointArc(l1 @ 1, (knob_base_radius + shoulder_radius, knob_body_height + shoulder_radius / 2), (knob_base_radius + shoulder_radius, knob_body_height + shoulder_radius))
            l3 = Line(l2 @ 1, (flange_radius, total_height))
            l4 = Line(l3 @ 1, (0, total_height))
            l5 = Line(l4 @ 1, (knob_base_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(shaft_hole_radius, total_height + 10)
solid_body = solid_body - Pos(0, 0, total_height - counterbore_depth / 2) * Cylinder(counterbore_radius, counterbore_depth)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
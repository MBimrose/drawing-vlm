from build123d import *

knob_total_length = 60.0
knob_body_radius = 12.0
knob_flange_radius = 22.0
knob_flange_thickness = 8.0
shoulder_fillet_radius = 6.0
thread_hole_diameter = 8.0
counterbore_diameter = 12.0
counterbore_depth = 3.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((knob_body_radius, 0), (knob_body_radius, knob_total_length - knob_flange_thickness - shoulder_fillet_radius))
            a1 = RadiusArc(l1 @ 1, (knob_body_radius + shoulder_fillet_radius, knob_total_length - knob_flange_thickness), shoulder_fillet_radius)
            l2 = Line(a1 @ 1, (knob_flange_radius, knob_total_length))
            l3 = Line(l2 @ 1, (0, knob_total_length))
            l4 = Line(l3 @ 1, (knob_body_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, knob_total_length / 2) * Cylinder(thread_hole_diameter / 2, knob_total_length + 10)
solid_body = solid_body - Pos(0, 0, knob_total_length - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
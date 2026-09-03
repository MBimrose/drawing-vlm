from build123d import *

knob_total_length = 40.0
shaft_radius = 12.0
flange_radius = 20.0
flange_thickness = 8.0
shoulder_radius = 16.0
shoulder_length = 6.0
thread_diameter = 8.0
thread_depth = 12.0
counterbore_diameter = 12.0
counterbore_depth = 3.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((shaft_radius, 0), (shaft_radius, knob_total_length - flange_thickness - shoulder_length))
            l2 = ThreePointArc(l1 @ 1, (shoulder_radius, knob_total_length - flange_thickness - shoulder_length + shoulder_length/2), (shoulder_radius, knob_total_length - flange_thickness))
            l3 = Line(l2 @ 1, (flange_radius, knob_total_length))
            l4 = Line(l3 @ 1, (0, knob_total_length))
            l5 = Line(l4 @ 1, (shaft_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, knob_total_length - thread_depth/2) * Cylinder(thread_diameter/2, thread_depth)
solid_body = solid_body - Pos(0, 0, knob_total_length - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "knob"
export_step(part, "output.step")
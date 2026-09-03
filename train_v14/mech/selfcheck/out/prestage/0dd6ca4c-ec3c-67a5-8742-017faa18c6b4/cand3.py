from build123d import *

base_radius = 15.0
base_height = 15.0
mid_radius = 25.0
mid_height = 40.0
top_radius = 10.0
total_height = 80.0
shaft_radius = 5.0
countersink_radius = 8.0
countersink_angle = 82.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (mid_radius, mid_height))
            l4 = Line(l3@1, (top_radius, total_height))
            l5 = Line(l4@1, (0, total_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(shaft_radius, total_height + 2)
solid_body = solid_body - Pos(0, 0, total_height) * CounterSinkHole(shaft_radius, countersink_radius, countersink_angle)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_profile_with_holes"
export_step(part, "output.step")
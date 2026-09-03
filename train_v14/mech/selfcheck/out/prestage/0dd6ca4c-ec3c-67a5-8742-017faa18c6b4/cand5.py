from build123d import *

total_length = 80.0
base_radius = 15.0
base_length = 20.0
mid_radius = 25.0
mid_length = 30.0
tip_radius = 10.0
tip_length = 30.0
bore_diameter = 10.0
countersink_diameter = 16.0
countersink_angle = 82.0
fillet_radius = 2.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_length))
            l3 = Line(l2 @ 1, (mid_radius, base_length + mid_length))
            l4 = Line(l3 @ 1, (tip_radius, total_length))
            l5 = Line(l4 @ 1, (0, total_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - CounterSinkHole(bore_diameter / 2, countersink_diameter / 2, total_length, countersink_angle)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

part = solid_body
part.name = "revolved_profile_with_hole"
export_step(part, "output.step")
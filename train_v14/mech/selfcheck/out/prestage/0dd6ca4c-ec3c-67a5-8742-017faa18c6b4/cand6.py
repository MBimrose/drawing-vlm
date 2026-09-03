from build123d import *

total_length = 80.0
base_radius = 15.0
tip_radius = 10.0
base_section_length = 15.0
outer_radius = 25.0
bore_radius = 5.0
base_chamfer = 2.0
tip_chamfer = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_section_length))
            l3 = Line(l2@1, (outer_radius, base_section_length))
            l4 = Line(l3@1, (tip_radius, total_length))
            l5 = Line(l4@1, (0, total_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(bore_radius, total_length + 2)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), base_chamfer)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), tip_chamfer)

part = solid_body
part.name = "revolved_profile_with_bore"
export_step(part, "output.step")
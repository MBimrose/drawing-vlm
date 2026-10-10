from build123d import *

base_radius = 30.0
top_radius = 35.0
base_height = 10.0
top_height = 10.0
transition_height = 20.0
wall_thickness = 3.0
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 20.0

total_height = base_height + transition_height + top_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_height))
            l3 = Line(l2 @ 1, (top_radius, base_height + transition_height))
            l4 = Line(l3 @ 1, (top_radius, total_height))
            l5 = Line(l4 @ 1, (0, total_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body - Pos(hole_offset, total_height / 2, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 10)

part = solid_body
part.name = "revolved_shell_with_hole"
export_step(part, "output.step")
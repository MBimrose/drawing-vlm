from build123d import *

base_radius = 30.0
top_radius = 45.0
height = 40.0
wall_thickness = 5.0
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, height * 0.3))
            l3 = Line(l2 @ 1, (top_radius, height))
            l4 = Line(l3 @ 1, (0, height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges(), fillet_radius)

hole = Pos(hole_offset, height / 2, height / 2) * Cylinder(hole_diameter / 2, height)
solid_body = solid_body - hole

part = solid_body
part.name = "revolved_shell_with_hole"
export_step(part, "output.step")
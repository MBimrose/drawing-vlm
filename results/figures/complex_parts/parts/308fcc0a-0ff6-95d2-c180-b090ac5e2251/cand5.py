from build123d import *

outer_base_radius = 30.0
outer_top_radius = 35.0
inner_base_radius = 25.0
inner_top_radius = 30.0
height = 40.0
shoulder_height = 10.0
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 20.0
hole_height = 20.0

with BuildPart() as outer_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_base_radius, 0))
            l2 = Line(l1 @ 1, (outer_base_radius, shoulder_height))
            l3 = Line(l2 @ 1, (outer_top_radius, height))
            l4 = Line(l3 @ 1, (0, height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

with BuildPart() as inner_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (inner_base_radius, 0))
            l2 = Line(l1 @ 1, (inner_base_radius, shoulder_height))
            l3 = Line(l2 @ 1, (inner_top_radius, height))
            l4 = Line(l3 @ 1, (0, height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = outer_bp.part - inner_bp.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole = Pos(hole_offset, hole_height, height / 2) * Cylinder(hole_diameter / 2, height)
solid_body = solid_body - hole

part = solid_body
part.name = "revolved_shell_with_hole"
export_step(part, "output.step")